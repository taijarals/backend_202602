"""
Mini prova service implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
import random
from fastapi import HTTPException, status
from models.miniprova import (
    QuestaoCreate, QuestaoResponse, QuestaoForStudent,
    MiniProvaCreate, MiniProvaUpdate, MiniProvaResponse, MiniProvaWithQuestoes,
    MiniProvaForStudent, TentativaCreate, TentativaResponse, TentativaWithDetails,
    RespostaCreate
)
from repositories import (
    MiniProvaRepository, QuestaoRepository,
    TentativaRepository, RespostaRepository
)
from .base import BaseService


class MiniProvaService(BaseService[MiniProvaResponse, MiniProvaRepository]):
    """Service for mini prova operations."""

    def __init__(self):
        super().__init__(MiniProvaRepository())
        self.questao_repo = QuestaoRepository()

    async def create_mini_prova(self, data: MiniProvaCreate) -> MiniProvaWithQuestoes:
        """Create mini prova with questions."""
        prova_data = data.model_dump(exclude={'questoes'})
        prova = await self.create(prova_data)

        # Create questions
        questoes = []
        for i, q in enumerate(data.questoes):
            q_data = q.model_dump()
            q_data['mini_prova_id'] = str(prova.id)
            q_data['ordem'] = i
            questao = await self.questao_repo.create(q_data)
            questoes.append(questao)

        return await self.get_with_questoes(prova.id)

    async def update_mini_prova(self, id: UUID, data: MiniProvaUpdate) -> MiniProvaResponse:
        """Update mini prova."""
        update_data = data.model_dump(exclude_unset=True)
        result = await self.update(id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Mini prova not found'
            )
        return result

    async def get_with_questoes(self, id: UUID, include_answers: bool = False) -> MiniProvaWithQuestoes:
        """Get mini prova with questions."""
        result = await self.repository.get_with_questoes(id, include_answers)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Mini prova not found'
            )
        return result

    async def get_for_student(self, id: UUID, aluno_id: UUID) -> MiniProvaForStudent:
        """Get mini prova for student taking."""
        result = await self.repository.get_for_student(id, aluno_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Mini prova not found'
            )

        # Check if student can attempt
        attempts = await self.repository.db.get_all(
            'tentativas_prova',
            filters={'mini_prova_id': str(id), 'aluno_id': str(aluno_id)}
        )
        completed_attempts = [a for a in attempts if a.get('status') == 'finalizada']

        if len(completed_attempts) >= result.tentativas_permitidas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Maximum attempts reached'
            )

        # Check time window
        now = datetime.utcnow()
        if result.inicio and now < result.inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Mini prova not yet available'
            )
        if result.fim and now > result.fim:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Mini prova has ended'
            )

        return result


class TentativaService(BaseService[TentativaResponse, TentativaRepository]):
    """Service for tentativa operations."""

    def __init__(self):
        super().__init__(TentativaRepository())
        self.resposta_repo = RespostaRepository()
        self.questao_repo = QuestaoRepository()

    async def start_tentativa(self, mini_prova_id: UUID, aluno_id: UUID) -> TentativaResponse:
        """Start a new test attempt."""
        # Check for active attempt
        active = await self.repository.get_active_attempt(mini_prova_id, aluno_id)
        if active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='You have an active attempt'
            )

        # Create attempt
        return await self.create({
            'mini_prova_id': str(mini_prova_id),
            'aluno_id': str(aluno_id),
            'inicio_em': datetime.utcnow().isoformat()
        })

    async def submit_answer(
        self,
        tentativa_id: UUID,
        questao_id: UUID,
        resposta: str
    ) -> Dict[str, Any]:
        """Submit an answer during attempt."""
        tentativa = await self.get_by_id(tentativa_id)
        if not tentativa or tentativa.status != 'em_andamento':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid attempt state'
            )

        # Save resposta
        saved = await self.resposta_repo.save_resposta(tentativa_id, questao_id, resposta)
        return saved

    async def finish_tentativa(self, tentativa_id: UUID) -> TentativaWithDetails:
        """Finish and grade attempt."""
        tentativa = await self.get_by_id(tentativa_id)
        if not tentativa or tentativa.status != 'em_andamento':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid attempt state'
            )

        # Get all respostas
        respostas = await self.resposta_repo.get_by_tentativa(tentativa_id)

        # Get questoes
        questoes = await self.questao_repo.get_by_mini_prova(tentativa.mini_prova_id)

        # Grade each answer
        total_points = 0
        for resp in respostas:
            questao = next((q for q in questoes if str(q.id) == str(resp.get('questao_id'))), None)
            if questao:
                correta = self._check_answer(questao, resp.get('resposta', ''))
                pontos = questao.pontos if correta else 0
                await self.resposta_repo.update_with_grading(resp['id'], correta, pontos)
                total_points += pontos

        # Calculate duration
        inicio = tentativa.inicio_em
        fim = datetime.utcnow()
        duration = int((fim - inicio).total_seconds())

        # Update tentativa
        await self.repository.finish_attempt(tentativa_id, total_points, duration)

        # Award points
        if total_points > 0:
            from repositories import PontuacaoRepository
            pontuacao_repo = PontuacaoRepository()
            await pontuacao_repo.add_points(
                aluno_id=tentativa.aluno_id,
                pontos=total_points,
                fonte='mini_prova',
                referencia_id=tentativa.mini_prova_id,
                descricao='Pontos de mini prova'
            )

            from services import UserService
            user_service = UserService()
            await user_service.add_points(tentativa.aluno_id, total_points)

        return await self.repository.get_with_details(tentativa_id)

    def _check_answer(self, questao: QuestaoResponse, resposta: str) -> bool:
        """Check if answer is correct."""
        if questao.tipo == 'multipla_escolha':
            return resposta.strip().lower() == questao.resposta_correta.strip().lower()
        elif questao.tipo == 'verdadeiro_falso':
            return resposta.strip().lower() == questao.resposta_correta.strip().lower()
        elif questao.tipo == 'resposta_curta':
            # Case insensitive comparison
            return resposta.strip().lower() == questao.resposta_correta.strip().lower()
        elif questao.tipo == 'codigo':
            # For code, we might need more sophisticated checking
            return resposta.strip() == questao.resposta_correta.strip()
        return False

    async def get_student_attempts(self, aluno_id: UUID, mini_prova_id: Optional[UUID] = None) -> List[TentativaWithDetails]:
        """Get student's attempts."""
        tentativas = await self.repository.get_by_aluno(aluno_id, mini_prova_id)
        return [await self.repository.get_with_details(t.id) for t in tentativas]

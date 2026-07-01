"""
Mini Prova repository implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from models.miniprova import (
    QuestaoResponse, QuestaoForStudent,
    MiniProvaResponse, MiniProvaWithQuestoes, MiniProvaForStudent,
    TentativaResponse, TentativaWithDetails
)
from .base import BaseRepository


class MiniProvaRepository(BaseRepository[MiniProvaResponse]):
    """Repository for mini prova operations."""

    def __init__(self):
        super().__init__('mini_provas', MiniProvaResponse)

    async def get_by_professor(self, professor_id: UUID) -> List[MiniProvaResponse]:
        """Get mini provas by professor."""
        return await self.get_all(filters={'professor_id': str(professor_id)}, order_by='-created_at')

    async def get_by_turma(self, turma_id: UUID) -> List[MiniProvaResponse]:
        """Get mini provas for a turma."""
        return await self.get_all(filters={'turma_id': str(turma_id), 'ativa': True})

    async def get_with_questoes(self, id: UUID, include_answers: bool = False) -> Optional[MiniProvaWithQuestoes]:
        """Get mini prova with questions."""
        result = await self.db.get_by_id(
            self.table,
            id,
            select='*,questoes(*),disciplinas(nome),turmas(nome)'
        )
        if result:
            data = result
            questoes = result.get('questoes', [])
            if not include_answers:
                # Remove correct answers for student view
                data['questoes'] = [
                    {k: v for k, v in q.items() if k != 'resposta_correta'}
                    for q in questoes
                ]
            else:
                data['questoes'] = questoes
            data['disciplina_nome'] = result.get('disciplinas', {}).get('nome') if result.get('disciplinas') else None
            data['turma_nome'] = result.get('turmas', {}).get('nome') if result.get('turmas') else None
            return MiniProvaWithQuestoes.model_validate(data)
        return None

    async def get_for_student(self, id: UUID, aluno_id: UUID) -> Optional[MiniProvaForStudent]:
        """Get mini prova for student view (no answers)."""
        prova = await self.get_with_questoes(id, include_answers=False)
        if not prova:
            return None
        # Get student's attempts
        tentativas = await self.db.get_all(
            'tentativas_prova',
            filters={
                'mini_prova_id': str(id),
                'aluno_id': str(aluno_id)
            }
        )
        # Convert to student view
        data = prova.model_dump()
        data['tentativas_realizadas'] = len([t for t in tentativas if t.get('status') == 'finalizada'])
        # Remove correct answers
        data['questoes'] = [
            QuestaoForStudent.model_validate(q).model_dump()
            for q in data.get('questoes', [])
        ]
        return MiniProvaForStudent.model_validate(data)

    async def get_active(self) -> List[MiniProvaResponse]:
        """Get all active mini provas."""
        now = datetime.utcnow()
        results = await self.get_all(filters={'ativa': True})
        # Filter by time window
        return [
            p for p in results
            if (p.inicio is None or p.inicio <= now) and
               (p.fim is None or p.fim >= now)
        ]


class QuestaoRepository(BaseRepository[QuestaoResponse]):
    """Repository for questao operations."""

    def __init__(self):
        super().__init__('questoes', QuestaoResponse)

    async def get_by_mini_prova(self, mini_prova_id: UUID, randomize: bool = False) -> List[QuestaoResponse]:
        """Get questions for a mini prova."""
        order_by = ' RANDOM()' if randomize else 'ordem'
        return await self.get_all(
            filters={'mini_prova_id': str(mini_prova_id)},
            order_by=order_by
        )

    async def get_for_student(self, mini_prova_id: UUID, randomize: bool = False) -> List[QuestaoForStudent]:
        """Get questions without answers for student."""
        questoes = await self.get_by_mini_prova(mini_prova_id, randomize)
        return [
            QuestaoForStudent(
                id=q.id,
                enunciado=q.enunciado,
                tipo=q.tipo,
                opcoes=q.opcoes,
                pontos=q.pontos,
                ordem=q.ordem
            )
            for q in questoes
        ]


class TentativaRepository(BaseRepository[TentativaResponse]):
    """Repository for tentativa operations."""

    def __init__(self):
        super().__init__('tentativas_prova', TentativaResponse)

    async def get_by_mini_prova(self, mini_prova_id: UUID) -> List[TentativaResponse]:
        """Get tentativas for a mini prova."""
        return await self.get_all(filters={'mini_prova_id': str(mini_prova_id)})

    async def get_by_aluno(self, aluno_id: UUID, mini_prova_id: Optional[UUID] = None) -> List[TentativaResponse]:
        """Get tentativas by aluno."""
        filters = {'aluno_id': str(aluno_id)}
        if mini_prova_id:
            filters['mini_prova_id'] = str(mini_prova_id)
        return await self.get_all(filters=filters, order_by='-created_at')

    async def get_active_attempt(self, mini_prova_id: UUID, aluno_id: UUID) -> Optional[TentativaResponse]:
        """Get active attempt for student."""
        return await self.get_one({
            'mini_prova_id': str(mini_prova_id),
            'aluno_id': str(aluno_id),
            'status': 'em_andamento'
        })

    async def get_attempts_count(self, mini_prova_id: UUID, aluno_id: UUID) -> int:
        """Get number of attempts for student."""
        return await self.count({
            'mini_prova_id': str(mini_prova_id),
            'aluno_id': str(aluno_id),
            'status': 'finalizada'
        })

    async def finish_attempt(self, id: UUID, points: int, duration: int) -> Optional[TentativaResponse]:
        """Finish an attempt with score."""
        return await self.update(id, {
            'status': 'finalizada',
            'pontos_obtidos': points,
            'tempo_gasto_segundos': duration,
            'fim_em': datetime.utcnow().isoformat()
        })

    async def get_with_details(self, id: UUID) -> Optional[TentativaWithDetails]:
        """Get tentativa with details."""
        result = await self.db.get_by_id(
            self.table,
            id,
            select='*,mini_provas(titulo),respostas_tentativa(*)'
        )
        if result:
            data = result
            data['mini_prova_titulo'] = result.get('mini_provas', {}).get('titulo') if result.get('mini_provas') else None
            data['respostas'] = result.get('respostas_tentativa', [])
            return TentativaWithDetails.model_validate(data)
        return None


class RespostaRepository(BaseRepository[Dict[str, Any]]):
    """Repository for resposta operations."""

    def __init__(self):
        super().__init__('respostas_tentativa', Dict[str, Any])

    async def save_resposta(self, tentativa_id: UUID, questao_id: UUID, resposta: str) -> Dict[str, Any]:
        """Save a resposta."""
        return await self.create({
            'tentativa_id': str(tentativa_id),
            'questao_id': str(questao_id),
            'resposta': resposta
        })

    async def get_by_tentativa(self, tentativa_id: UUID) -> List[Dict[str, Any]]:
        """Get all respostas for a tentativa."""
        return await self.get_all(filters={'tentativa_id': str(tentativa_id)})

    async def update_with_grading(self, id: UUID, correta: bool, pontos: int) -> Dict[str, Any]:
        """Update resposta with grading result."""
        return await self.update(id, {'correta': correta, 'pontos_obtidos': pontos})

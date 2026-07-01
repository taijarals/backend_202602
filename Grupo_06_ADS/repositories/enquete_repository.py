"""
Enquete repository implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from models.enquete import (
    OpcaoEnqueteResponse,
    EnqueteResponse, EnqueteWithOpcoes,
    VotoEnqueteResponse, EnqueteStats
)
from .base import BaseRepository


class EnqueteRepository(BaseRepository[EnqueteResponse]):
    """Repository for enquete operations."""

    def __init__(self):
        super().__init__('enquetes', EnqueteResponse)

    async def get_by_professor(self, professor_id: UUID) -> List[EnqueteResponse]:
        """Get enquetes by professor."""
        return await self.get_all(filters={'professor_id': str(professor_id)}, order_by='-created_at')

    async def get_by_turma(self, turma_id: UUID) -> List[EnqueteResponse]:
        """Get enquetes for a turma."""
        return await self.get_all(filters={'turma_id': str(turma_id), 'ativa': True}, order_by='-created_at')

    async def get_with_opcoes(self, id: UUID) -> Optional[EnqueteWithOpcoes]:
        """Get enquete with opcoes and vote counts."""
        result = await self.db.get_by_id(
            self.table,
            id,
            select='*,profiles!professor_id(nome),turmas(nome)'
        )
        if result:
            data = result
            data['professor_nome'] = result.get('profiles', {}).get('nome') if result.get('profiles') else None
            data['turma_nome'] = result.get('turmas', {}).get('nome') if result.get('turmas') else None
            # Get opcoes with vote counts
            opcoes_result = await self.db.get_all(
                'opcoes_enquete',
                filters={'enquete_id': str(id)},
                order_by='ordem'
            )
            # Count votes for each option
            opcoes = []
            total_votes = 0
            for opcao in opcoes_result:
                votes = await self.db.count('votos_enquete', {'opcao_id': opcao['id']})
                opcao['votos'] = votes
                total_votes += votes
                opcoes.append(OpcaoEnqueteResponse.model_validate(opcao))
            data['opcoes'] = opcoes
            data['total_votos'] = total_votes
            return EnqueteWithOpcoes.model_validate(data)
        return None

    async def get_active(self) -> List[EnqueteResponse]:
        """Get all active enquetes."""
        now = datetime.utcnow()
        results = await self.get_all(filters={'ativa': True})
        return [
            e for e in results
            if e.fim is None or e.fim >= now
        ]


class OpcaoEnqueteRepository(BaseRepository[OpcaoEnqueteResponse]):
    """Repository for opcao enquete operations."""

    def __init__(self):
        super().__init__('opcoes_enquete', OpcaoEnqueteResponse)

    async def get_by_enquete(self, enquete_id: UUID) -> List[OpcaoEnqueteResponse]:
        """Get opcoes for an enquete."""
        return await self.get_all(filters={'enquete_id': str(enquete_id)}, order_by='ordem')

    async def create_many(self, enquete_id: UUID, textos: List[str]) -> List[OpcaoEnqueteResponse]:
        """Create multiple opcoes for an enquete."""
        opcoes = []
        for i, texto in enumerate(textos):
            opcao = await self.create({
                'enquete_id': str(enquete_id),
                'texto': texto,
                'ordem': i
            })
            opcoes.append(opcao)
        return opcoes


class VotoEnqueteRepository(BaseRepository[VotoEnqueteResponse]):
    """Repository for voto enquete operations."""

    def __init__(self):
        super().__init__('votos_enquete', VotoEnqueteResponse)

    async def get_by_enquete(self, enquete_id: UUID) -> List[VotoEnqueteResponse]:
        """Get all votos for an enquete."""
        results = await self.db.get_all(
            self.table,
            filters={'enquete_id': str(enquete_id)},
            select='*,opcoes_enquete(texto)'
        )
        items = []
        for r in results:
            r['opcao_texto'] = r.get('opcoes_enquete', {}).get('texto') if r.get('opcoes_enquete') else None
            items.append(VotoEnqueteResponse.model_validate(r))
        return items

    async def has_voted(self, enquete_id: UUID, aluno_id: UUID) -> bool:
        """Check if aluno has voted in enquete."""
        result = await self.get_one({'enquete_id': str(enquete_id), 'aluno_id': str(aluno_id)})
        return result is not None

    async def cast_vote(self, enquete_id: UUID, opcao_id: UUID, aluno_id: UUID) -> VotoEnqueteResponse:
        """Cast a vote."""
        return await self.create({
            'enquete_id': str(enquete_id),
            'opcao_id': str(opcao_id),
            'aluno_id': str(aluno_id)
        })

    async def get_stats(self, enquete_id: UUID, turma_id: Optional[UUID] = None) -> EnqueteStats:
        """Get enquete statistics."""
        votos = await self.get_by_enquete(enquete_id)

        # Get opcoes with counts
        opcao_repo = OpcaoEnqueteRepository()
        opcoes = await opcao_repo.get_by_enquete(enquete_id)

        opcoes_stats = []
        for opcao in opcoes:
            vote_count = sum(1 for v in votos if str(v.opcao_id) == str(opcao.id))
            percentage = (vote_count / len(votos) * 100) if votos else 0
            opcoes_stats.append({
                'opcao_id': str(opcao.id),
                'texto': opcao.texto,
                'votos': vote_count,
                'percentual': round(percentage, 2)
            })

        # Calculate participation
        total_votos = len(votos)
        participacao = 0.0
        if turma_id:
            from database import get_db
            db = get_db()
            turma_count = db.table('turma_alunos').select('id', count='exact').eq('turma_id', str(turma_id)).execute()
            total_students = turma_count.count or 0
            participacao = (total_votos / total_students * 100) if total_students > 0 else 0

        return EnqueteStats(
            enquete_id=enquete_id,
            total_votos=total_votos,
            participacao_percentual=participacao,
            opcoes_stats=opcoes_stats
        )

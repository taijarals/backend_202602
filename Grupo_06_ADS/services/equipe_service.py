"""
Equipe service implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
import random
from fastapi import HTTPException, status
from models.equipe import (
    EquipeCreate, EquipeUpdate, EquipeResponse,
    EquipeMembroResponse, EquipeWithDetails,
    EquipeMembroCreate, TeamFormationRequest, TeamFormationResult
)
from repositories import EquipeRepository, EquipeMembroRepository, TurmaAlunoRepository
from .base import BaseService


class EquipeService(BaseService[EquipeResponse, EquipeRepository]):
    """Service for equipe operations."""

    def __init__(self):
        super().__init__(EquipeRepository())
        self.membro_repo = EquipeMembroRepository()
        self.turma_aluno_repo = TurmaAlunoRepository()

    async def create_equipe(self, data: EquipeCreate) -> EquipeWithDetails:
        """Create a new equipe."""
        equipe = await self.create(data.model_dump())
        return await self.get_with_members(equipe.id)

    async def get_with_members(self, id: UUID) -> EquipeWithDetails:
        """Get equipe with members."""
        result = await self.repository.get_with_members(id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Equipe not found'
            )
        return result

    async def get_by_turma(self, turma_id: UUID) -> List[EquipeWithDetails]:
        """Get all equipes for a turma with members."""
        equipes = await self.repository.get_by_turma(turma_id)
        results = []
        for e in equipes:
            details = await self.repository.get_with_members(e.id)
            if details:
                results.append(details)
        return results

    async def add_member(self, equipe_id: UUID, aluno_id: UUID, papel: str = 'membro') -> EquipeMembroResponse:
        """Add member to equipe."""
        # Check equipe exists
        equipe = await self.get_by_id(equipe_id)
        if not equipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Equipe not found'
            )

        # Check member count
        current_count = await self.membro_repo.get_member_count(equipe_id)
        if current_count >= equipe.max_membros:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Equipe is full'
            )

        # Check if already in an equipe for this turma
        existing = await self.membro_repo.get_aluno_equipe(aluno_id, equipe.turma_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Student is already in an equipe for this turma'
            )

        return await self.membro_repo.add_member(equipe_id, aluno_id, papel)

    async def remove_member(self, equipe_id: UUID, aluno_id: UUID) -> bool:
        """Remove member from equipe."""
        return await self.membro_repo.remove_member(equipe_id, aluno_id)

    async def get_student_equipe(self, aluno_id: UUID, turma_id: Optional[UUID] = None) -> Optional[EquipeWithDetails]:
        """Get student's equipe for a turma."""
        membro = await self.membro_repo.get_aluno_equipe(aluno_id, turma_id)
        if membro:
            return await self.get_with_members(membro.equipe_id)
        return None

    async def auto_form_teams(self, request: TeamFormationRequest) -> TeamFormationResult:
        """Automatically form teams for a turma."""
        # Get all students in turma
        students = await self.turma_aluno_repo.get_students_by_turma(request.turma_id)
        if not students:
            return TeamFormationResult(
                equipes_criadas=0,
                equipes=[],
                alunos_sem_equipe=[]
            )

        # Sort by criteria
        if request.criterio == 'pontuacao':
            # Sort by points to balance teams
            students = sorted(students, key=lambda x: x.aluno_pontos or 0, reverse=True)
        elif request.criterio == 'habilidade':
            # Could implement skill-based sorting
            students = sorted(students, key=lambda x: x.aluno_pontos or 0, reverse=True)
        else:
            # Random shuffle
            random.shuffle(students)

        # Determine number of equipes
        num_equipes = request.numero_equipes or max(1, len(students) // request.membros_por_equipe)

        # Create equipes
        equipes = []
        for i in range(num_equipes):
            cor = self._get_color_for_index(i)
            equipe = await self.create({
                'nome': f'Equipe {i + 1}',
                'turma_id': str(request.turma_id),
                'max_membros': request.membros_por_equipe,
                'cor': cor
            })
            equipes.append(equipe)

        # Distribute students using snake draft for balance
        alunos_sem_equipe = []
        for i, student in enumerate(students):
            # Snake pattern: 0,1,2,3,3,2,1,0,0,1,...
            cycle = (i // num_equipes) % 2
            pos_in_cycle = i % num_equipes
            equipe_idx = pos_in_cycle if cycle == 0 else (num_equipes - 1 - pos_in_cycle)

            if equipe_idx < len(equipes):
                try:
                    await self.membro_repo.add_member(equipes[equipe_idx].id, student.aluno_id)
                except Exception:
                    alunos_sem_equipe.append(student.aluno_id)
            else:
                alunos_sem_equipe.append(student.aluno_id)

        # Get updated equipes with members
        equipes_with_members = [await self.get_with_members(e.id) for e in equipes]

        return TeamFormationResult(
            equipes_criadas=len(equipes),
            equipes=[e for e in equipes_with_members if e],
            alunos_sem_equipe=alunos_sem_equipe
        )

    def _get_color_for_index(self, index: int) -> str:
        """Get team color based on index."""
        colors = [
            '#3B82F6', '#EF4444', '#10B981', '#F59E0B',
            '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
        ]
        return colors[index % len(colors)]

    async def update_equipe_points(self, equipe_id: UUID, points: int) -> EquipeResponse:
        """Update equipe total points."""
        result = await self.repository.update_points(equipe_id, points)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Equipe not found'
            )
        return result

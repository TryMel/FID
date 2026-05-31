from pydantic import BaseModel
from typing import List, Optional


class UserStats(BaseModel):
    total_users: int
    active_users: int
    freelance_count: int
    client_count: int


class DashboardStats(BaseModel):
    total_revenue: float
    active_projects: int
    pending_verifications: int
    recent_registrations: int


class UserManagement(BaseModel):
    id: str
    email: str
    nom: str
    role: str
    statut: str
    date_creation: str

from sqlmodel import Session, select

from app.models.documents import Project, ProjectCreate, ProjectTypeEnum


def create_project(session: Session, project_create: ProjectCreate) -> Project:
    db_obj = Project.model_validate(project_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_project_by_name_type(
    session: Session, name: str, type: ProjectTypeEnum
) -> Project | None:
    statement = select(Project).where(
        Project.name == name, Project.type == type, Project.is_delete != True  # noqa: E712
    )
    session_proj = session.exec(statement).first()
    return session_proj


def get_or_create_project(
    session: Session, name: str, type: ProjectTypeEnum, iscuser_id: str
) -> tuple[Project, bool]:
    db_proj = get_project_by_name_type(session, name, type)

    created = False

    if not db_proj:
        created = True
        proj_create = ProjectCreate(name=name, type=type, iscuser_id=iscuser_id)
        db_proj = create_project(session, proj_create)

    return db_proj, created

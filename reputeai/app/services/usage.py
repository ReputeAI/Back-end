from datetime import datetime
from sqlalchemy.orm import Session

from ..models.usage import Usage


def log_usage(db: Session, org_id: int, units: int = 1) -> None:
    month = datetime.utcnow().strftime("%Y-%m")
    usage = (
        db.query(Usage)
        .filter(Usage.org_id == org_id, Usage.month == month)
        .first()
    )
    if usage is None:
        usage = Usage(org_id=org_id, month=month, units=0)
        db.add(usage)
    usage.units += units
    db.commit()

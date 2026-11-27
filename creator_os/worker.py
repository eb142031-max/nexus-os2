"""Durable scheduler worker: turns due automation rules into draft jobs only.

It never calls generation providers and never spends provider credits.
Run a single worker against PostgreSQL; SQLite is for local single-process evaluation.
"""
from datetime import timedelta
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from app import AutomationRule, AuditEvent, GenerationJob, SessionLocal, utcnow

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("darkleyla.worker")

def enqueue_due_drafts():
    db = SessionLocal()
    try:
        now = utcnow()
        due = (db.query(AutomationRule)
            .filter(AutomationRule.enabled.is_(True), AutomationRule.next_run_at <= now)
            .with_for_update(skip_locked=True).all())
        count = 0
        for rule in due:
            job = GenerationJob(avatar_id=rule.avatar_id, prompt=rule.prompt_template,
                mode=rule.mode, aspect_ratio=rule.aspect_ratio,
                state="draft_pending_manual_execution")
            rule.last_run_at = now
            rule.next_run_at = now + timedelta(minutes=rule.interval_minutes)
            db.add(job)
            db.flush()
            db.add(AuditEvent(actor_key_id=None, event="automation.draft_enqueued",
                object_type="generation_job", object_id=job.id,
                details='{"automation_id":"' + rule.id + '"}'))
            count += 1
        db.commit()
        if count:
            log.info("Enqueued %s generation draft(s). No provider calls were made.", count)
    except Exception:
        db.rollback()
        log.exception("Automation tick failed")
    finally:
        db.close()

if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(enqueue_due_drafts, "interval", seconds=30,
        id="darkleyla-draft-scheduler", max_instances=1, coalesce=True)
    log.info("Dark Leyla draft scheduler started.")
    scheduler.start()

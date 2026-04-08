from __future__ import annotations

from ugc_ai_influencer.models import JobRecord, JobStatus


def build_start_message() -> str:
    return (
        "Send product text, a website link, a YouTube/blog URL, or a product image and I will turn it into "
        "a UGC ad package with angles, scripts, shot plan, and render instructions."
    )


def build_image_prompt(caption: str | None, image_analysis: str) -> str:
    intro = caption.strip() if caption and caption.strip() else "Create a UGC ad from this product image."
    return f"{intro}\n\nImage analysis: {image_analysis}"


def build_job_reply(job: JobRecord) -> str:
    if job.status == JobStatus.FAILED:
        return f"Job {job.job_id} failed: {job.error_message}"

    assert job.source_brief is not None
    assert job.strategy is not None
    assert job.script_package is not None
    assert job.media_artifact is not None

    preview_scripts = "\n\n".join(
        f"{index}. {script}"
        for index, script in enumerate(job.script_package.scripts, start=1)
    )
    return (
        f"Job {job.job_id} is ready.\n"
        f"Product: {job.source_brief.product}\n"
        f"Audience: {job.source_brief.audience}\n"
        f"Primary angle: {job.strategy.primary_angle}\n"
        f"CTA: {job.strategy.cta}\n"
        f"Render package: {job.media_artifact.package_path}\n\n"
        f"Script options:\n{preview_scripts}"
    )

from flask import Flask, render_template, request, send_file
from xhtml2pdf import pisa
import io
import json

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = {
        "name":           request.form.get("name", "").strip(),
        "email":          request.form.get("email", ""),
        "phone":          request.form.get("phone", ""),
        "linkedin":       request.form.get("linkedin", ""),
        "github":         request.form.get("github", ""),
        "jobtitle":       request.form.get("jobtitle", ""),
        "summary":        request.form.get("summary", ""),
        "skills":         request.form.get("skills", ""),
        "achievements":   request.form.get("achievements", ""),
        "certifications": request.form.get("certifications", ""),
        "languages":      request.form.get("languages", ""),
    }

    # ── Experience — multiple jobs ──
    companies    = request.form.getlist("company")
    roles        = request.form.getlist("role")
    durations    = request.form.getlist("duration")
    descriptions = request.form.getlist("description")

    experiences = []
    for i in range(len(companies)):
        if companies[i].strip():
            bullet_points = [b.strip() for b in descriptions[i].split("\n") if b.strip()]
            experiences.append({
                "company":  companies[i],
                "role":     roles[i],
                "duration": durations[i],
                "bullets":  bullet_points
            })
    data["experiences"] = experiences

    # ── Projects — structured JSON from JS ──
    try:
        raw_projects = request.form.get("projects_json", "[]")
        projects = json.loads(raw_projects)
        # filter out blank entries
        projects = [p for p in projects if p.get("title", "").strip()]
    except (json.JSONDecodeError, TypeError):
        projects = []
    data["projects"] = projects

    # ── Education — structured JSON from JS ──
    try:
        raw_education = request.form.get("education_json", "[]")
        education = json.loads(raw_education)
        education = [e for e in education if e.get("degree", "").strip() or e.get("college", "").strip()]
    except (json.JSONDecodeError, TypeError):
        education = []
    data["education"] = education

    # ── Render HTML → PDF ──
    html_content = render_template("resume_template.html", **data)
    pdf_buffer = io.BytesIO()
    result = pisa.CreatePDF(html_content, dest=pdf_buffer)

    if result.err:
        return "PDF generation failed. Please try again or contact support.", 500

    pdf_buffer.seek(0)

    # Safe filename — fallback to HireBait_Resume if name is blank
    safe_name = data["name"] if data["name"] else "HireBait_Resume"
    safe_name = safe_name.replace(" ", "_")

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{safe_name}_resume.pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)

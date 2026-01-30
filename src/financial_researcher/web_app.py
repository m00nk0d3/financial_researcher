"""Flask web application for Financial Researcher."""
import os
import threading
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import markdown2
import time

from financial_researcher.job_manager import JobManager, JobState
from financial_researcher.crew_runner import run_crew_with_logging


app = Flask(__name__)
job_manager = JobManager()


@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


@app.route('/research', methods=['POST'])
def start_research():
    """Start a new research job."""
    data = request.get_json()
    
    if not data or 'company' not in data:
        return jsonify({'error': 'Company name is required'}), 400
    
    company_name = data['company'].strip()
    
    if not company_name:
        return jsonify({'error': 'Company name cannot be empty'}), 400
    
    # Validate company name (basic sanitization)
    if len(company_name) > 100:
        return jsonify({'error': 'Company name too long (max 100 characters)'}), 400
    
    # Create job
    job_id = job_manager.create_job(company_name)
    
    # Start crew execution in background thread
    thread = threading.Thread(
        target=run_crew_with_logging,
        args=(company_name, job_manager, job_id),
        daemon=True
    )
    thread.start()
    
    return jsonify({'job_id': job_id, 'company': company_name}), 202


@app.route('/stream/<job_id>')
def stream_job(job_id: str):
    """Server-Sent Events endpoint for job progress."""
    job = job_manager.get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    def generate():
        """Generate SSE events for job progress."""
        last_log_count = 0
        
        while True:
            job = job_manager.get_job(job_id)
            if not job:
                yield f"event: error\ndata: Job not found\n\n"
                break
            
            # Send new logs
            logs = job.logs[last_log_count:]
            for log in logs:
                yield f"event: log\ndata: {log}\n\n"
            last_log_count = len(job.logs)
            
            # Send status updates
            yield f"event: status\ndata: {job.state.value}\n\n"
            
            # Check if job is complete
            if job.state == JobState.COMPLETED:
                yield f"event: complete\ndata: {job.report_path}\n\n"
                break
            elif job.state == JobState.FAILED:
                error_msg = job.error_message or "Unknown error"
                yield f"event: error\ndata: {error_msg}\n\n"
                break
            
            # Wait before next check
            time.sleep(0.5)
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@app.route('/report/<job_id>')
def get_report(job_id: str):
    """Get the final report as HTML."""
    job = job_manager.get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job.state != JobState.COMPLETED:
        return jsonify({'error': 'Job not completed yet'}), 400
    
    if not job.report_path:
        return jsonify({'error': 'Report not available'}), 404
    
    # Read markdown file
    report_file = Path(job.report_path)
    if not report_file.exists():
        return jsonify({'error': 'Report file not found'}), 404
    
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown2.markdown(
            markdown_content,
            extras=['tables', 'fenced-code-blocks', 'header-ids']
        )
        
        return jsonify({'html': html_content, 'company': job.company_name})
    except Exception as e:
        return jsonify({'error': f'Error reading report: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


def run_web_app(host='127.0.0.1', port=5000, debug=False):
    """Run the Flask web application."""
    print(f"Starting Financial Researcher Web Interface...")
    print(f"Open your browser to: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_web_app(debug=True)

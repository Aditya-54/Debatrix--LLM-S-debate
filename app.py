from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from main import DebateSystem
from summary import DebateSystem as DocDebateSystem
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'debatix-secret-key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Gemini client
try:
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel('gemini-1.5-pro')
except Exception as e:
    print(f"Error initializing Gemini client: {str(e)}")
    gemini_model = None

# Initialize the debate systems
debate_system = DebateSystem()
doc_debate_system = DocDebateSystem()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/debate', methods=['GET', 'POST'])
def debate():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            topic = data.get('topic', '')
            if topic:
                try:
                    debate_result = debate_system.run_full_debate(topic)
                    return jsonify(debate_result)
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            else:
                return jsonify({'error': 'No topic provided'}), 400
    return render_template('debate.html')

@app.route('/document-debate', methods=['GET', 'POST'])
def document_debate():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            action = data.get('action')
            debate_id = data.get('debate_id')
            
            if action == 'next':
                try:
                    subtopic = data.get('subtopic', '')
                    if not subtopic:
                        return jsonify({'error': 'Please provide a subtopic'}), 400
                        
                    # Get the current debate
                    debate = doc_debate_system.context_manager.get_debate(debate_id)
                    if not debate:
                        return jsonify({'error': 'Debate not found'}), 404
                    
                    # Verify file exists
                    if not os.path.exists(debate['document_path']):
                        return jsonify({'error': 'Document file not found'}), 404
                        
                    # Generate response for the subtopic
                    result = doc_debate_system.run_debate_round(debate_id, "subtopic", subtopic)
                    return jsonify({'result': result})
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            
            elif action == 'rebuttal':
                try:
                    # Get the current debate
                    debate = doc_debate_system.context_manager.get_debate(debate_id)
                    if not debate:
                        return jsonify({'error': 'Debate not found'}), 404
                    
                    # Verify file exists
                    if not os.path.exists(debate['document_path']):
                        return jsonify({'error': 'Document file not found'}), 404
                        
                    # Get the current round to determine if it's a subtopic
                    current_round = doc_debate_system.context_manager.get_current_round(debate_id)
                    if current_round and current_round.get('type') == 'subtopic_statement':
                        # If the current round is a subtopic, generate a rebuttal for that subtopic
                        result = doc_debate_system.run_debate_round(debate_id, "rebuttal", current_round.get('subtopic'))
                    else:
                        # Otherwise, generate a regular rebuttal
                        result = doc_debate_system.run_debate_round(debate_id, "rebuttal")
                    return jsonify({'result': result})
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            
            elif action == 'judge':
                try:
                    result = doc_debate_system.generate_judge_evaluation(debate_id)
                    # Clean up the file after judge evaluation
                    debate = doc_debate_system.context_manager.get_debate(debate_id)
                    if debate and 'document_path' in debate:
                        try:
                            os.remove(debate['document_path'])
                        except:
                            pass
                    return jsonify({'result': result})
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            
            return jsonify({'error': 'Invalid action'}), 400
        
        # Handle form data submission
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                # Create a unique filename to avoid conflicts
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                    filename = f"{base}_{counter}{ext}"
                    counter += 1
                
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Ensure the upload directory exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # Save the file
                file.save(filepath)
                
                if not os.path.exists(filepath):
                    return jsonify({'error': 'Failed to save file'}), 500
                
                prompt = request.form.get('prompt', '')
                role = request.form.get('role', '')
                
                if not prompt or not role:
                    os.remove(filepath)
                    return jsonify({'error': 'Please provide both a prompt and select a role'}), 400
                
                try:
                    debate_id = doc_debate_system.start_new_debate(filepath, prompt, role)
                    result = doc_debate_system.run_debate_round(debate_id, "initial")
                    return jsonify({
                        'debate_id': debate_id,
                        'result': result
                    })
                except Exception as e:
                    os.remove(filepath)  # Clean up if there's an error
                    return jsonify({'error': str(e)}), 500
                    
            except Exception as e:
                return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    return render_template('document_debate.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/debate/start', methods=['POST'])
def start_debate():
    if request.is_json:
        data = request.get_json()
        topic = data.get('topic', '')
        if topic:
            try:
                # Initialize debate context
                debate_context = {
                    'topic': topic,
                    'rounds': [],
                    'current_side': 'pro',  # Start with pro side
                    'status': 'active'
                }
                
                # Store debate context in session
                session['debate_context'] = debate_context
                
                return jsonify({
                    'message': f'Debate started on topic: "{topic}". Click "Pro Argument" to begin.'
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'No topic provided'}), 400
    return jsonify({'error': 'Invalid request'}), 400

@app.route('/debate/pro', methods=['POST'])
def get_pro_argument():
    if request.is_json:
        data = request.get_json()
        topic = data.get('topic', '')
        round_num = data.get('round', 0)
        
        if not topic:
            return jsonify({'error': 'No topic provided'}), 400
            
        try:
            if not gemini_model:
                return jsonify({'error': 'Gemini model not initialized. Please check your API key.'}), 500
                
            # Get debate context
            debate_context = session.get('debate_context', {})
            if not debate_context or debate_context.get('topic') != topic:
                return jsonify({'error': 'Debate not found or topic mismatch'}), 400
                
            # Use Gemini 1.5 for web search and argument generation
            prompt = f"""You are a professional debater arguing in favor of the topic: {topic}
            
            Requirements:
            1. Generate a strong, evidence-based argument
            2. Include specific examples and data
            3. Use web search to find relevant sources and citations
            4. Format the response with clear points and proper citations
            
            Current debate round: {round_num + 1}
            
            Previous rounds: {json.dumps(debate_context.get('rounds', []))}
            
            Generate a comprehensive argument with proper citations:"""
            
            try:
                response = gemini_model.generate_content(prompt)
                if not response or not response.text:
                    raise ValueError("Empty response from Gemini model")
                    
                # Extract citations from the response
                citations = []
                argument_text = response.text
                
                # Update debate context
                debate_context['rounds'].append({
                    'side': 'pro',
                    'round': round_num + 1,
                    'argument': argument_text,
                    'citations': citations
                })
                debate_context['current_side'] = 'con'
                session['debate_context'] = debate_context
                
                return jsonify({
                    'argument': argument_text,
                    'citations': citations
                })
                
            except Exception as e:
                print(f"Error generating content: {str(e)}")
                return jsonify({'error': f'Error generating argument: {str(e)}'}), 500
                
        except Exception as e:
            print(f"Error in get_pro_argument: {str(e)}")
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Invalid request'}), 400

@app.route('/debate/con', methods=['POST'])
def get_con_argument():
    if request.is_json:
        data = request.get_json()
        topic = data.get('topic', '')
        round_num = data.get('round', 0)
        
        if not topic:
            return jsonify({'error': 'No topic provided'}), 400
            
        try:
            if not gemini_model:
                return jsonify({'error': 'Gemini model not initialized. Please check your API key.'}), 500
                
            # Get debate context
            debate_context = session.get('debate_context', {})
            if not debate_context or debate_context.get('topic') != topic:
                return jsonify({'error': 'Debate not found or topic mismatch'}), 400
                
            # Use Gemini 1.5 for web search and argument generation
            prompt = f"""You are a professional debater arguing against the topic: {topic}
            
            Requirements:
            1. Generate a strong, evidence-based counter-argument
            2. Address points made in previous rounds
            3. Include specific examples and data
            4. Use web search to find relevant sources and citations
            5. Format the response with clear points and proper citations
            
            Current debate round: {round_num + 1}
            
            Previous rounds: {json.dumps(debate_context.get('rounds', []))}
            
            Generate a comprehensive counter-argument with proper citations:"""
            
            try:
                response = gemini_model.generate_content(prompt)
                if not response or not response.text:
                    raise ValueError("Empty response from Gemini model")
                    
                # Extract citations from the response
                citations = []
                argument_text = response.text
                
                # Update debate context
                debate_context['rounds'].append({
                    'side': 'con',
                    'round': round_num + 1,
                    'argument': argument_text,
                    'citations': citations
                })
                debate_context['current_side'] = 'pro'
                session['debate_context'] = debate_context
                
                return jsonify({
                    'argument': argument_text,
                    'citations': citations
                })
                
            except Exception as e:
                print(f"Error generating content: {str(e)}")
                return jsonify({'error': f'Error generating argument: {str(e)}'}), 500
                
        except Exception as e:
            print(f"Error in get_con_argument: {str(e)}")
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Invalid request'}), 400

@app.route('/debate/judge', methods=['POST'])
def get_judgment():
    if request.is_json:
        data = request.get_json()
        topic = data.get('topic', '')
        rounds = data.get('rounds', 0)
        
        if not topic:
            return jsonify({'error': 'No topic provided'}), 400
            
        try:
            if not gemini_model:
                return jsonify({'error': 'Gemini model not initialized. Please check your API key.'}), 500
                
            # Get debate context
            debate_context = session.get('debate_context', {})
            if not debate_context or debate_context.get('topic') != topic:
                return jsonify({'error': 'Debate not found or topic mismatch'}), 400
                
            # Use Gemini 1.5 for judgment
            prompt = f"""You are an expert debate judge evaluating the following debate:

Topic: {topic}
Number of rounds: {rounds}

Debate rounds:
{json.dumps(debate_context.get('rounds', []), indent=2)}

Please provide a comprehensive judgment that includes:
1. Analysis of each side's strongest arguments
2. Evaluation of evidence and citations used
3. Assessment of argument structure and delivery
4. Final verdict with clear reasoning
5. Suggestions for improvement

Format your response clearly with these sections:"""
            
            try:
                response = gemini_model.generate_content(prompt)
                if not response or not response.text:
                    raise ValueError("Empty response from Gemini model")
                    
                # Clear debate context
                session.pop('debate_context', None)
                
                return jsonify({
                    'judgment': response.text
                })
                
            except Exception as e:
                print(f"Error generating content: {str(e)}")
                return jsonify({'error': f'Error generating judgment: {str(e)}'}), 500
                
        except Exception as e:
            print(f"Error in get_judgment: {str(e)}")
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Invalid request'}), 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}

if __name__ == '__main__':
    app.run(debug=True) 
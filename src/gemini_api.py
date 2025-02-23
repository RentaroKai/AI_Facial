import os
import certifi
import httplib2
from pathlib import Path
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

# Configure the Gemini API with company's SSL support
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("APIキーが設定されていません")

cert_path = os.environ.get("SSL_CERT_FILE")
if cert_path:
    cert_path_obj = Path(cert_path)
    if not cert_path_obj.exists():
        raise FileNotFoundError(f"SSL証明書が見つかりません: {cert_path}")
    httplib2.CA_CERTS = str(cert_path_obj)
    print(f"DEBUG: Using company SSL certificate: {cert_path}")
else:
    default_cert = certifi.where()
    os.environ["SSL_CERT_FILE"] = default_cert
    os.environ["REQUESTS_CA_BUNDLE"] = default_cert
    print(f"DEBUG: Using system default certificate: {default_cert}")

genai.configure(api_key=api_key, transport="rest")
print("DEBUG: Gemini API configured")

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini and returns the response.

    Args:
        path (str): Path to the image file
        mime_type (str, optional): MIME type of the file. Defaults to None.

    Returns:
        FileData: Uploaded file data object with uri and display_name
    """
    print(f"DEBUG: Starting upload_to_gemini for path: {path}")
    if mime_type is None:
        mime_type = "image/jpeg"  # Default to JPEG
        print("DEBUG: MIME type not provided, defaulting to 'image/jpeg'")
    else:
        print(f"DEBUG: Provided MIME type: {mime_type}")

    print(f"DEBUG: Checking if file exists at: {path}")
    if not Path(path).exists():
        print(f"DEBUG: File not found at: {path}")
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")

    try:
        print("DEBUG: Attempting to upload file...")
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"DEBUG: Successfully uploaded file '{file.display_name}' as: {file.uri}")
        return file
    except Exception as e:
        print(f"DEBUG: Exception occurred during upload: {str(e)}")
        raise

def analyze_expression(file_obj):
    import google.generativeai as genai
    from google.ai.generativelanguage_v1beta.types import content

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_schema": content.Schema(
            type=content.Type.OBJECT,
            enum=[],
            required=["表情の名前", "言いそうなセリフ"],
            properties={
                "表情の名前": content.Schema(
                    type=content.Type.STRING,
                ),
                "言いそうなセリフ": content.Schema(
                    type=content.Type.STRING,
                ),
            },
        ),
        "response_mime_type": "application/json",
    }

    system_instruction = "このキャラクタがどのような感情でいるのかを、表情解析して複雑なニュアンスについてよく考えてください。その後、この表情を表す名前(感情の強弱について必ず言及すること)と、この表情で言いそうなセリフを生成してください。（例：照れて少しムスっとする/\"うっるせえっ\" 小さいｓ悲しげな驚き/\"え…そうなの？\"強い怒りをうちに秘めている /\"(なんだと…！)\"　弱々しく苦笑い /\"そうかもね・・・\""
    try:
        print(f"DEBUG: Starting chat session for file: {file_obj.display_name}")
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
            system_instruction=system_instruction,
        )
        chat_history = [{
            "role": "user",
            "parts": [
                file_obj,
                "解析せよ"
            ],
        }]
        print(f"DEBUG: Chat history: {chat_history}")
        chat_session = model.start_chat(history=chat_history)
        response = chat_session.send_message("INSERT_INPUT_HERE")
        print(f"DEBUG: Chat response: {response.text}")
        return response
    except Exception as e:
        print(f"DEBUG: Error in analyze_expression: {str(e)}")
        raise
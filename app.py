import streamlit as st
from openai import OpenAI  # ← FORMA NOVA!
import re
from pypdf import PdfReader

# Configuração da página
st.set_page_config(page_title="Carbon Due Diligence AI", page_icon="🌳")

# Título do seu site
st.title("🌳 Carbon Due Diligence AI")
st.markdown("**Analise PDDs de créditos de carbono em 60 segundos**")

# Sidebar para a chave da API
with st.sidebar:
    st.header("🔑 Configuração")
    api_key = st.text_input("Cole sua OpenAI API Key:", type="password")
    st.markdown("[Obtenha sua chave aqui](https://platform.openai.com/api-keys)")
    st.markdown("---")
    st.info("Sua chave não é salva e some quando você fecha a página.")

# Função para extrair PDF
def extrair_texto_pdf(pdf_file):
    try:
        leitor = PdfReader(pdf_file)
        texto_total = ""
        for pagina in leitor.pages:
            texto = pagina.extract_text()
            if texto:
                texto_total += texto + "\n"
        return texto_total if texto_total else None
    except Exception as e:
        st.error(f"Erro ao ler PDF: {str(e)}")
        return None

def encontrar_secao_adicionalidade(texto):
    padroes = [
        r'additionalit[y|ie][\s\S]{1,1500}(?=\n\s*\n|\n[A-Z]|$)',
        r'adicionalidade[\s\S]{1,1500}(?=\n\s*\n|\n[A-Z]|$)',
    ]
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group().strip()
    return texto[:4000]

# Área principal do site
st.subheader("📤 Faça upload do PDD (PDF)")

uploaded_file = st.file_uploader("Escolha o arquivo PDF do projeto", type="pdf")

if uploaded_file is not None and api_key:
    
    with st.spinner("🔍 Analisando o documento..."):
        
        texto_completo = extrair_texto_pdf(uploaded_file)
        
        if texto_completo:
            secao_adicionalidade = encontrar_secao_adicionalidade(texto_completo)
            
            if len(secao_adicionalidade) > 100:
                
                try:
                    # ⭐⭐ FORMA NOVA - OpenAI v1.0.0 ⭐⭐
                    client = OpenAI(api_key=api_key)  # ← Cria o cliente
                    
                    prompt = f"""
                    Analise esta seção de ADICIONALIDADE de um projeto de carbono e responda em PORTUGUÊS:

                    TEXTO: {secao_adicionalidade[:3000]}

                    FORMATO DA RESPOSTA:
                    **Score:** X/10
                    **Pontos Fortes:** 
                    - ...
                    **Pontos Fracos:**
                    - ...
                    **Recomendação:** [APROVAR/ANALISAR MAIS/REJEITAR]
                    """
                    
                    # ⭐⭐ FORMA NOVA de chamar a API ⭐⭐
                    resposta = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
                    
                    # ⭐⭐ FORMA NOVA de pegar a resposta ⭐⭐
                    resultado = resposta.choices[0].message.content
                    
                    st.success("✅ Análise concluída!")
                    st.subheader("📊 Resultado:")
                    st.markdown(resultado)
                    
                    # Mostra um resumo visual do score
                    if "**Score:**" in resultado:
                        try:
                            score_texto = resultado.split("**Score:**")[1].split("/")[0].strip()
                            score = int(score_texto)
                            if score <= 3:
                                st.balloons()
                                st.success("🎉 Projeto de Baixo Risco!")
                            elif score <= 7:
                                st.warning("⚠️ Projeto de Risco Moderado")
                            else:
                                st.error("🚨 Projeto de Alto Risco")
                        except:
                            pass
                            
                except Exception as e:
                    st.error(f"Erro na análise: {str(e)}")
            else:
                st.error("Seção de adicionalidade não encontrada.")
        else:
            st.error("Não foi possível ler o PDF.")

elif uploaded_file and not api_key:
    st.warning("⚠️ Cole sua OpenAI API Key na sidebar")

else:
    st.markdown("""
    ### 🤔 Como usar:
    1. **Obtenha uma API Key** da OpenAI
    2. **Cole a API Key** na sidebar
    3. **Faça upload do PDD** em PDF
    4. **Receba a análise em segundos**
    
    *Exemplo de PDDs para testar: [Verra Registry](https://registry.verra.org/app/search/VCS)*
    """)

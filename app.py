import streamlit as st
import PyPDF2
import openai
import re
import os

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

# Funções do sistema (MESMO CÓDIGO do script anterior)
def extrair_texto_pdf(pdf_file):
    try:
        leitor = PyPDF2.PdfReader(pdf_file)
        texto_total = ""
        for pagina in leitor.pages:
            texto = pagina.extract_text()
            if texto:
                texto_total += texto + "\n"
        return texto_total if texto_total else None
    except Exception as e:
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
    
    # Mostra que está processando
    with st.spinner("🔍 Analisando o documento..."):
        
        # Extrai texto do PDF
        texto_completo = extrair_texto_pdf(uploaded_file)
        
        if texto_completo:
            # Encontra a seção de adicionalidade
            secao_adicionalidade = encontrar_secao_adicionalidade(texto_completo)
            
            if len(secao_adicionalidade) > 100:
                
                # Configura a chave da API
                openai.api_key = api_key
                
                # Analisa com a IA
                try:
                    prompt = f"""
                    Você é um especialista em créditos de carbono. Analise a seção de ADICIONALIDADE abaixo e dê um score de 1 a 10 (1=excelente, 10=péssimo).

                    CRITÉRIOS:
                    - O projeto prova que NÃO existiria sem os créditos?
                    - A análise financeira é robusta?
                    - As barreiras são bem explicadas?

                    TEXTO:
                    {secao_adicionalidade[:3000]}

                    RESPONDA EM PORTUGUÊS NO FORMATO:
                    Score: X/10
                    Pontos Fortes: 
                    - ...
                    Pontos Fracos:
                    - ...
                    Recomendação: [APROVAR/ANALISAR MAIS/REJEITAR]
                    """
                    
                    resposta = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
                    
                    resultado = resposta.choices[0].message.content
                    
                    # Mostra os resultados
                    st.success("✅ Análise concluída!")
                    st.subheader("📊 Resultado:")
                    st.write(resultado)
                    
                    # Mostra um resumo visual do score
                    if "Score:" in resultado:
                        score_texto = resultado.split("Score:")[1].split("/")[0].strip()
                        try:
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
                st.error("Não foi possível encontrar a seção de adicionalidade no documento.")
        else:
            st.error("Não foi possível ler o PDF. O arquivo pode estar corrompido ou ser uma imagem.")

elif uploaded_file and not api_key:
    st.warning("⚠️ Por favor, cole sua OpenAI API Key na sidebar")

else:
    # Instruções quando não há arquivo
    st.markdown("""
    ### 🤔 Como usar:
    1. **Obtenha uma API Key** da OpenAI (link na sidebar)
    2. **Cole a API Key** no campo à esquerda
    3. **Faça upload do PDD** em PDF
    4. **Receba a análise em segundos**
    
    ### 📈 O que você recebe:
    - ✅ **Score de risco** (1-10)
    - ✅ **Pontos fortes e fracos**
    - ✅ **Recomendação final**
    
    *Exemplo de PDDs para testar: [Verra Registry](https://registry.verra.org/app/search/VCS)*
    """)
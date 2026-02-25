import streamlit as st
import requests
import whois
import re
import pandas as pd
from email import policy
from email.parser import BytesParser
from io import BytesIO
from datetime import datetime
# For simple NLP urgency detection
from textblob import TextBlob 

# --- CONFIGURATION ---
st.set_page_config(page_title="SOC Phishing Analyzer", layout="wide", page_icon="🛡️")

# --- UTILITY FUNCTIONS ---

def parse_raw_email(raw_email):
    """Parses raw email string to extract headers and body."""
    try:
        msg = BytesParser().parsebytes(raw_email.encode('utf-8'))
        subject = msg['subject']
        sender = msg['from']
        receiver = msg['to']
        date = msg['date']
        
        # Extract body (simple get_payload for now, can be improved)
        body = msg.get_body(preferencelist=('plain')).get_content()
        
        return {
            "subject": subject,
            "sender": sender,
            "receiver": receiver,
            "date": date,
            "body": body,
            "headers": dict(msg.items())
        }
    except Exception as e:
        st.error(f"Error parsing email: {e}")
        return None

def extract_urls(text):
    """Extracts URLs from text using Regex."""
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\$\\$,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return re.findall(url_pattern, text)

def check_virustotal(domain_or_ip, vt_api_key, resource_type="ip"):
    """Checks reputation on VirusTotal."""
    url = "https://www.virustotal.com/api/v3/"
    headers = {"x-apikey": vt_api_key}
    
    if resource_type == "ip":
        endpoint = f"ip_addresses/{domain_or_ip}"
    else:
        endpoint = f"domains/{domain_or_ip}"
        
    try:
        response = requests.get(url + endpoint, headers=headers)
        if response.status_code == 200:
            data = response.json()["data"]["attributes"]
            last_analysis_stats = data.get("last_analysis_stats", {})
            malicious = last_analysis_stats.get("malicious", 0)
            suspicious = last_analysis_stats.get("suspicious", 0)
            total_engines = sum(last_analysis_stats.values())
            return {
                "malicious": malicious,
                "suspicious": suspicious,
                "total": total_engines,
                "reputation": data.get("reputation", 0),
                "tags": data.get("tags", [])
            }
        return None
    except Exception as e:
        return {"error": str(e)}

def get_domain_age(domain):
    """Checks domain creation date using WHOIS."""
    try:
        w = whois.whois(domain)
        if w.creation_date:
            if isinstance(w.creation_date, list):
                creation_date = w.creation_date[0]
            else:
                creation_date = w.creation_date
            
            age = datetime.now() - creation_date
            return age.days
    except:
        return None

def analyze_urgency(text):
    """Simple NLP to detect urgent language (Phishing indicator)."""
    analysis = TextBlob(text)
    urgency_keywords = ["urgent", "immediate", "verify", "suspend", "account", "password", "bank", "lock"]
    score = 0
    found_keywords = []
    
    for word in urgency_keywords:
        if word in text.lower():
            score += 1
            found_keywords.append(word)
            
    return score, found_keywords

# --- MAIN DASHBOARD UI ---

st.title("🛡️ SOC Phishing Email Analyzer")
st.markdown("Paste the **Raw Email Source** (Headers + Body) to analyze potential threats.")

# Sidebar for API Keys
st.sidebar.header("⚙️ Configuration")
vt_api_key = st.sidebar.text_input("VirusTotal API Key", type="password")

if not vt_api_key:
    st.sidebar.warning("Please enter your VirusTotal API Key to enable reputation checks.")

# Input Area
raw_email_input = st.text_area("Paste Raw Email Here:", height=300, placeholder="Delivered-To: analyst@soc.com...")

if st.button("🚀 Analyze Email"):
    if not raw_email_input:
        st.error("Please paste an email first.")
    else:
        with st.spinner("Parsing and Analyzing..."):
            # 1. Parse Email
            email_data = parse_raw_email(raw_email_input)
            
            if email_data:
                col1, col2 = st.columns([1, 2])
                
                # --- SECTION: METADATA & HEADERS ---
                with col1:
                    st.subheader("📧 Header Info")
                    st.write(f"**From:** {email_data['sender']}")
                    st.write(f"**To:** {email_data['receiver']}")
                    st.write(f"**Subject:** {email_data['subject']}")
                    
                    # Check SPF/DKIM
                    auth_results = email_data['headers'].get('Authentication-Results', 'N/A')
                    st.info(f"Auth Results: {auth_results}")

                # --- SECTION: THREAT ANALYSIS ---
                with col2:
                    st.subheader("🚨 Threat Analysis")
                    
                    # 1. NLP Urgency Check
                    score, keywords = analyze_urgency(email_data['body'] + email_data['subject'])
                    if score > 0:
                        st.warning(f"⚠️ High Urgency Detected! ({score} triggers)")
                        st.write(f"Keywords found: {', '.join(keywords)}")
                    
                    # 2. Extract & Check Links
                    urls = extract_urls(email_data['body'])
                    st.write(f"**Found {len(urls)} URLs in body.**")
                    
                    if urls and vt_api_key:
                        # Show a sample of URLs
                        unique_urls = list(set(urls))[:5] # Limit to 5 for demo speed
                        
                        for url in unique_urls:
                            st.write(f"Analyzing: `{url[:50]}...`")
                            # Simple domain extraction for VT
                            try:
                                domain = url.split('/')[2]
                                # Basic check if it's an IP or Domain
                                if not domain.replace(".","").isdigit():
                                    vt_result = check_virustotal(domain, vt_api_key, "domain")
                                    if vt_result:
                                        if "error" in vt_result:
                                            st.error(vt_result["error"])
                                        else:
                                            if vt_result["malicious"] > 0:
                                                st.error(f"❌ MALICIOUS ({vt_result['malicious']}/{vt_result['total']} engines)")
                                            elif vt_result["suspicious"] > 0:
                                                st.warning(f"⚠️ SUSPICIOUS ({vt_result['suspicious']} engines)")
                                            else:
                                                st.success(f"✅ Clean ({vt_result['reputation']} Rep)")
                                            
                                            # Domain Age Check
                                            age = get_domain_age(domain)
                                            if age is not None:
                                                if age < 30:
                                                    st.error(f"⚠️ New Domain! Created {age} days ago.")
                                                else:
                                                    st.caption(f"Domain Age: {age} days")
                            except:
                                pass

                    # 3. Sender Domain Reputation
                    # Extract sender email address
                    sender_addr = re.search(r'<(.+?)>', email_data['sender'])
                    if sender_addr:
                        sender_email = sender_addr.group(1)
                    else:
                        sender_email = email_data['sender']

                    if "@" in sender_email:
                        sender_domain = sender_email.split("@")[1]
                        if vt_api_key:
                            st.write(f"Checking sender domain: {sender_domain}")
                            dom_result = check_virustotal(sender_domain, vt_api_key, "domain")
                            if dom_result and "error" not in dom_result:
                                if dom_result["malicious"] > 0:
                                    st.error(f"🚫 Sender Domain MALICIOUS")
                                else:
                                    st.success(f"✅ Sender Domain Reputation: {dom_result['reputation']}")

                # --- SECTION: RAW DATA ---
                with st.expander("View Parsed Details"):
                    st.json(email_data)

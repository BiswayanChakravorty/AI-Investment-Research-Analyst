import re
from .models import ToneAnalysis,ToneSentence
POSITIVE={"strong","growth","record","improving","robust","healthy","demand","upside","confident"}
NEGATIVE={"weak","decline","declining","pressure","risk","uncertain","headwind","slower","downside"}
GUIDANCE=[r"expect",r"expects",r"guidance",r"outlook",r"forecast",r"project",r"we see",r"we anticipate",r"margin",r"revenue"]
def split_sentences(text): return [s.strip() for s in re.split(r"(?<=[.!?])\s+",text or "") if s.strip()]
def sentence_sentiment(sentence):
 w={x.lower() for x in re.findall(r"[A-Za-z]+",sentence)}; pos=len(w&POSITIVE); neg=len(w&NEGATIVE); return max(-1,min(1,(pos-neg)/max(3,pos+neg+1)))
def classify_topic(sentence):
 s=sentence.lower()
 if any(k in s for k in ("revenue","demand","orders","sales")): return "growth"
 if any(k in s for k in ("margin","cost","gross profit","operating")): return "profitability"
 if any(k in s for k in ("capex","capacity","factory","investment")): return "capital_allocation"
 if any(k in s for k in ("competition","competitor","pricing")): return "competition"
 if any(k in s for k in ("regulation","export","geopolitical")): return "macro_regulatory"
 return "general"
def guidance_signal(sentence): return any(re.search(p,sentence.lower()) for p in GUIDANCE)
def analyze_transcript(text):
 rows=[]
 for s in split_sentences(text):
  sentiment=sentence_sentiment(s); guidance=guidance_signal(s); topic=classify_topic(s); weight=(2 if guidance else 1)*(1.25 if topic in {"growth","profitability"} else 1); rows.append(ToneSentence(text=s,sentiment=sentiment,topic=topic,guidance=guidance,weight=weight))
 if not rows:return ToneAnalysis()
 mti=sum(x.sentiment*x.weight for x in rows)/sum(x.weight for x in rows); return ToneAnalysis(current_mti=round(mti,4),sentences=rows)
def compare_tone(current,prior):
 current.prior_mti=prior.current_mti
 if current.current_mti is not None and prior.current_mti is not None: current.delta_mti=round(current.current_mti-prior.current_mti,4)
 return current

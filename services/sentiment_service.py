from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

model_id = "koohk/KcELECTRA_v1"  

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSequenceClassification.from_pretrained(model_id)
model.eval()

label_map = {0: "부정", 1: "긍정"}

def predict_single(text: str):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)
        pred = torch.argmax(probs, dim=-1).item()
        confidence = round(probs[0][pred].item(), 4)

    return {
        "text": text,
        "label": label_map[pred],
        "confidence": confidence
    }


def analyze_messages(messages: list):
    results = []
    
    for msg in messages:
        result = predict_single(msg)
        if result["confidence"] >= 0.9:
            results.append(result)

    total_valid = len(results)
    positive_count = sum(1 for r in results if r["label"] == "긍정")
    positive_ratio = round(positive_count / total_valid * 100, 2) if total_valid > 0 else None

    # 댓글이 10개 초과일 경우, results는 숨김 처리
    if len(messages) > 10:
        return {
            "count": len(messages),
            "valid_results": total_valid,
            "positive_ratio": positive_ratio
        }
    else:
        return {
            "count": len(messages),
            "valid_results": total_valid,
            "positive_ratio": positive_ratio,
            "results": results
        }
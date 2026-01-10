# ============================
# AI PPT PIPELINE – SINGLE FILE
# ============================

import json
from typing import List, TypedDict
# ---------- LANGGRAPH ----------
from langgraph.graph import StateGraph, END


# ============================
# 1️⃣ STATE DEFINITION
# ============================

class SlideState(TypedDict):
    outline: List[dict]
    slides: List[dict]
    feedback: List[dict]
    approved: bool


# ============================
# 2️⃣ LANGGRAPH NODES
# ============================

def generate_slides(state: SlideState):
    """LLM slide generation node"""
    slides = []

    for s in state["outline"]:
        slides.append({
            "title": s["title"],
            "content": (
                f"• Concept explanation of {s['title']}\n"
                f"• Simple example\n"
                f"• Diagram suggestion"
            ),
            "approved": False
        })

    return {
        "slides": slides,
        "approved": False
    }


def review_slides(state: SlideState):
    """
    Professor / LLM critic node
    Replace logic with UI feedback or rubric-based LLM
    """
    feedback = []
    approved = True

    for slide in state["slides"]:
        # Example quality rule
        if "advanced" in slide["content"].lower():
            approved = False
            feedback.append({
                "title": slide["title"],
                "comment": "Simplify this slide for undergraduate level"
            })
        else:
            slide["approved"] = True

    return {
        "feedback": feedback,
        "approved": approved
    }


def revise_slides(state: SlideState):
    """Auto-revision node"""
    for slide in state["slides"]:
        for fb in state["feedback"]:
            if slide["title"] == fb["title"]:
                slide["content"] += (
                    "\n• Simplified explanation added\n"
                    "• Extra intuitive example"
                )
                slide["approved"] = True

    return {
        "slides": state["slides"],
        "approved": True
    }


def decision(state: SlideState):
    """Loop controller"""
    if state["approved"]:
        return END
    return "revise_slides"


# ============================
# 3️⃣ BUILD LANGGRAPH
# ============================

workflow = StateGraph(SlideState)

workflow.add_node("generate_slides", generate_slides)
workflow.add_node("review_slides", review_slides)
workflow.add_node("revise_slides", revise_slides)

workflow.set_entry_point("generate_slides")

workflow.add_edge("generate_slides", "review_slides")
workflow.add_conditional_edges(
    "review_slides",
    decision,
    {
        END: END,
        "revise_slides": "revise_slides"
    }
)
workflow.add_edge("revise_slides", "review_slides")

graph = workflow.compile()


# ============================
# 4️⃣ DJANGO API ENDPOINTS
# ============================

@csrf_exempt
def generate_outline(request):
    """
    STEP 1: Outline generation
    Plug FAISS + embeddings here
    """
    outline = [
        {"title": "Introduction", "points": ["Definition", "Importance"]},
        {"title": "Core Concepts", "points": ["Architecture", "Workflow"]},
        {"title": "Examples", "points": ["Use cases", "Case study"]},
        {"title": "Challenges", "points": ["Limitations", "Ethics"]},
        {"title": "Conclusion", "points": ["Summary", "Future scope"]}
    ]

    return JsonResponse({"outline": outline})


@csrf_exempt
def generate_slides_api(request):
    """
    STEP 2: LangGraph-powered slide generation + review loop
    """
    body = json.loads(request.body)

    result = graph.invoke({
        "outline": body["outline"],
        "slides": [],
        "feedback": [],
        "approved": False
    })

    return JsonResponse({
        "slides": result["slides"]
    })


@csrf_exempt
def render_ppt(request):
    """
    STEP 3: PPT rendering
    Replace with python-pptx
    """
    body = json.loads(request.body)
    slides = body["slides"]

    # Placeholder PPT generation
    # python-pptx goes here

    return JsonResponse({
        "ppt_url": "/media/final_presentation.pptx",
        "slides_rendered": len(slides)
    })


# ============================
# 5️⃣ OPTIONAL: URLS (COPY)
# ============================
"""
from django.urls import path
from pipeline import generate_outline, generate_slides_api, render_ppt

urlpatterns = [
    path("api/generate-outline/", generate_outline),
    path("api/generate-slides/", generate_slides_api),
    path("api/render-ppt/", render_ppt),
]
"""

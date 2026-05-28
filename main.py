import asyncio
import httpx
from fastapi import FastAPI, Query
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def fetch_repo(client: httpx.AsyncClient, user: str, repo_name: str):
    try:
        response = await client.get(
            f"https://api.github.com/repos/{user}/{repo_name}",
            headers={"Accept": "application/vnd.github.v3+json"}
        )
        if response.status_code != 200:
            return {
                "name": repo_name,
                "description": "Repository not found or API rate limit exceeded.",
                "language": "Unknown",
                "stargazers_count": 0
            }
        data = response.json()
        return {
            "name": data.get("name", repo_name),
            "description": data.get("description") or "",
            "language": data.get("language") or "Unknown",
            "stargazers_count": data.get("stargazers_count", 0)
        }
    except Exception:
        return {
            "name": repo_name,
            "description": "Error fetching data.",
            "language": "Unknown",
            "stargazers_count": 0
        }

def get_lang_color(lang: str) -> str:
    colors = {
        "Python": "#3572A5",
        "JavaScript": "#f1e05a",
        "TypeScript": "#3178c6",
        "CSS": "#563d7c",
        "HTML": "#e34c26",
        "Java": "#b07219",
        "C++": "#f34b7d",
        "C": "#555555",
        "C#": "#178600",
        "PHP": "#4F5D95",
        "Go": "#00ADD8",
        "Rust": "#dea584",
        "Ruby": "#701516",
    }
    return colors.get(lang, "#cccccc")

def escape_xml(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

@app.get("/api/svg")
async def generate_svg(user: str = Query(...), repos: str = Query(...)):
    repo_names = [r.strip() for r in repos.split(",")]
    
    async with httpx.AsyncClient() as client:
        tasks = [fetch_repo(client, user, repo) for repo in repo_names]
        repo_data_list = await asyncio.gather(*tasks)

    title_height = 100
    repo_height = 110
    total_height = title_height + (len(repo_data_list) * repo_height) + 20

    svg = f"""
    <svg width="800" height="{total_height}" viewBox="0 0 800 {total_height}" fill="none" xmlns="http://www.w3.org/2000/svg">
      <style>
        .title {{ font: 400 26px 'Segoe UI', Ubuntu, Sans-Serif; fill: #ffffff; }}
        .repo-name {{ font: 400 20px 'Segoe UI', Ubuntu, Sans-Serif; fill: #48B9C7; }}
        .repo-desc {{ font: 400 13px 'Segoe UI', Ubuntu, Sans-Serif; fill: #C9D1D9; }}
        .repo-meta {{ font: 400 12px 'Segoe UI', Ubuntu, Sans-Serif; fill: #8B949E; }}
      </style>
      
      <rect x="0.5" y="0.5" width="799" height="{total_height - 1}" fill="#0d1117" rx="8" stroke="#30363d"/>
      
      <text x="40" y="60" class="title">Other projects by me</text>
    """

    current_y = title_height
    for i, repo in enumerate(repo_data_list):
        is_last = (i == len(repo_data_list) - 1)
        
        name = escape_xml(repo["name"])
        desc = escape_xml(repo["description"])
        if len(desc) > 85:
            desc = desc[:82] + "..."
            
        lang = escape_xml(repo["language"])
        color = get_lang_color(repo["language"])
        stars = repo["stargazers_count"]

        svg += f"""
        <text x="140" y="{current_y + 20}" class="repo-name">{name}</text>
        <text x="140" y="{current_y + 45}" class="repo-desc">{desc}</text>
        
        <circle cx="145" cy="{current_y + 70}" r="5" fill="{color}" />
        <text x="156" y="{current_y + 74}" class="repo-meta">{lang}</text>
        
        <g transform="translate(225, {current_y + 62})">
          <path fill-rule="evenodd" clip-rule="evenodd" fill="#8B949E" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25zm0 2.445L6.615 5.5a.75.75 0 01-.564.41l-3.097.45 2.24 2.184a.75.75 0 01.216.664l-.528 3.084 2.769-1.456a.75.75 0 01.698 0l2.77 1.456-.53-3.084a.75.75 0 01.216-.664l2.24-2.183-3.096-.45a.75.75 0 01-.564-.41L8 2.694v.001z" />
        </g>
        <text x="245" y="{current_y + 74}" class="repo-meta">{stars}</text>
        """

        if not is_last:
            svg += f'<line x1="130" y1="{current_y + 95}" x2="670" y2="{current_y + 95}" stroke="#30363d" stroke-width="1"/>'

        current_y += repo_height

    svg += "</svg>"

    return Response(content=svg, media_type="image/svg+xml", headers={
        "Cache-Control": "public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400"
    })

# Mount static files to serve frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

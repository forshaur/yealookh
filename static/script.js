document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.getElementById('usernameInput');
    const fetchBtn = document.getElementById('fetchBtn');
    const errorMsg = document.getElementById('errorMsg');
    const reposSection = document.getElementById('reposSection');
    const reposGrid = document.getElementById('reposGrid');
    const generateBtn = document.getElementById('generateBtn');
    const resultSection = document.getElementById('resultSection');
    const svgUrlSpan = document.getElementById('svgUrl');
    const copyBtn = document.getElementById('copyBtn');
    const previewImage = document.getElementById('previewImage');

    let currentUsername = '';
    let reposData = [];
    let selectedRepos = new Set();

    const getLangColor = (lang) => {
        const colors = {
            Python: "#3572A5",
            JavaScript: "#f1e05a",
            TypeScript: "#3178c6",
            CSS: "#563d7c",
            HTML: "#e34c26",
            Java: "#b07219",
            "C++": "#f34b7d",
            C: "#555555",
            "C#": "#178600",
            PHP: "#4F5D95",
            Go: "#00ADD8",
            Rust: "#dea584",
            Ruby: "#701516",
        };
        return colors[lang] || "#cccccc";
    };

    const fetchRepos = async () => {
        const username = usernameInput.value.trim();
        if (!username) return;

        fetchBtn.textContent = 'Fetching...';
        fetchBtn.disabled = true;
        errorMsg.style.display = 'none';
        reposSection.style.display = 'none';
        resultSection.style.display = 'none';
        selectedRepos.clear();
        reposGrid.innerHTML = '';
        currentUsername = username;

        try {
            const res = await fetch(`https://api.github.com/users/${username}/repos?per_page=100&sort=updated`);
            if (!res.ok) {
                throw new Error("Failed to fetch repositories. Check username or API rate limits.");
            }
            reposData = await res.json();
            
            if (reposData.length === 0) {
                throw new Error("No public repositories found for this user.");
            }

            renderRepos();
            reposSection.style.display = 'block';
            updateGenerateBtn();
        } catch (err) {
            errorMsg.textContent = err.message;
            errorMsg.style.display = 'block';
        } finally {
            fetchBtn.textContent = 'Fetch Repos';
            fetchBtn.disabled = false;
        }
    };

    const toggleSelection = (repoName, cardEl, checkbox) => {
        if (selectedRepos.has(repoName)) {
            selectedRepos.delete(repoName);
            cardEl.classList.remove('selected');
            checkbox.checked = false;
        } else {
            selectedRepos.add(repoName);
            cardEl.classList.add('selected');
            checkbox.checked = true;
        }
        updateGenerateBtn();
    };

    const updateGenerateBtn = () => {
        generateBtn.disabled = selectedRepos.size === 0;
        if (selectedRepos.size > 0) {
            generateBtn.textContent = `Generate SVG URL (${selectedRepos.size} selected)`;
        } else {
            generateBtn.textContent = `Generate SVG URL`;
        }
    };

    const renderRepos = () => {
        reposData.forEach(repo => {
            const card = document.createElement('div');
            card.className = 'repo-card';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'checkbox';
            checkbox.readOnly = true;

            const info = document.createElement('div');
            info.className = 'repo-info';

            const name = document.createElement('div');
            name.className = 'repo-name';
            name.textContent = repo.name;

            const desc = document.createElement('div');
            desc.className = 'repo-desc';
            desc.textContent = repo.description || "No description provided.";

            const meta = document.createElement('div');
            meta.className = 'repo-meta';

            if (repo.language) {
                const langItem = document.createElement('div');
                langItem.className = 'meta-item';
                
                const dot = document.createElement('span');
                dot.className = 'lang-dot';
                dot.style.backgroundColor = getLangColor(repo.language);
                
                langItem.appendChild(dot);
                langItem.appendChild(document.createTextNode(repo.language));
                meta.appendChild(langItem);
            }

            const starsItem = document.createElement('div');
            starsItem.className = 'meta-item';
            starsItem.textContent = `⭐ ${repo.stargazers_count}`;
            meta.appendChild(starsItem);

            info.appendChild(name);
            info.appendChild(desc);
            info.appendChild(meta);

            card.appendChild(checkbox);
            card.appendChild(info);

            card.addEventListener('click', () => toggleSelection(repo.name, card, checkbox));
            
            reposGrid.appendChild(card);
        });
    };

    const generateSvg = () => {
        if (selectedRepos.size === 0) return;
        
        const origin = window.location.origin;
        const repoList = Array.from(selectedRepos).join(",");
        const url = `${origin}/api/svg?user=${currentUsername}&repos=${repoList}`;
        
        svgUrlSpan.textContent = url;
        previewImage.src = url;
        resultSection.style.display = 'flex';
    };

    const copyUrl = () => {
        navigator.clipboard.writeText(svgUrlSpan.textContent);
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        setTimeout(() => {
            copyBtn.textContent = originalText;
        }, 2000);
    };

    fetchBtn.addEventListener('click', fetchRepos);
    usernameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') fetchRepos();
    });
    generateBtn.addEventListener('click', generateSvg);
    copyBtn.addEventListener('click', copyUrl);
});

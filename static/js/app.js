const noteForm = document.getElementById("note-form");
const noteTitleInput = document.getElementById("note-title");
const noteUrlInput = document.getElementById("note-url");
const noteContentInput = document.getElementById("note-content");
const notesContainer = document.getElementById("notes-container");
const emptyState = document.getElementById("empty-state");

document.addEventListener("DOMContentLoaded", fetchNotes);

async function fetchNotes() {
    if (!notesContainer) return;
    try {
        const res = await fetch("/api/notes");
        const notes = await res.json();
        renderNotes(notes);
    } catch (err) {
        console.error("Failed to load notes:", err);
    }
}

function renderNotes(notes) {
    notesContainer.innerHTML = "";
    if (notes.length === 0) {
        emptyState.style.display = "block";
        return;
    }
    emptyState.style.display = "none";

    notes.forEach(note => {
        const card = document.createElement("div");
        card.className = "card note-card";
        card.style.cursor = "pointer";

        // Clicking anywhere on the card opens its separate editor page
        card.addEventListener("click", (e) => {
            // Prevent opening editor if they specifically clicked the URL link button or Delete button
            if (e.target.closest(".note-link-btn") || e.target.closest(".btn-danger")) {
                return;
            }
            window.location.href = `/note/${note.id}`;
        });

        let linkHtml = "";
        if (note.url) {
            const formattedUrl = note.url.startsWith("http://") || note.url.startsWith("https://") 
                ? note.url 
                : `https://${note.url}`;
            linkHtml = `
                <div>
                    <a href="${escapeHtml(formattedUrl)}" target="_blank" rel="noopener noreferrer" class="note-link-btn" onclick="event.stopPropagation();">
                        🔗 Open Link
                    </a>
                </div>
            `;
        }

        card.innerHTML = `
            <div>
                <h3 class="note-title">${escapeHtml(note.title)}</h3>
                ${linkHtml}
                <p class="note-content">${escapeHtml(note.content)}</p>
            </div>
            <div>
                <div class="note-meta">TIMESTAMP: ${note.updated_at}</div>
                <div class="note-actions">
                    <span style="font-size: 0.75rem; color: var(--neon-cyan); margin-right: auto; align-self: center;">CLICK CARD TO EDIT &rarr;</span>
                    <button class="btn btn-danger" onclick="event.stopPropagation(); deleteNote(${note.id})">Delete</button>
                </div>
            </div>
        `;
        notesContainer.appendChild(card);
    });
}

// Add new note from the Dashboard form
if (noteForm) {
    noteForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const title = noteTitleInput.value.trim();
        const url = noteUrlInput.value.trim();
        const content = noteContentInput.value.trim();

        if (!title || !content) return;

        const payload = { title, content, url };

        try {
            const res = await fetch("/api/notes", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error("Create failed");

            // Clear inputs
            noteTitleInput.value = "";
            noteUrlInput.value = "";
            noteContentInput.value = "";
            fetchNotes();
        } catch (err) {
            alert(err.message);
        }
    });
}

// Quick delete directly from Dashboard
async function deleteNote(id) {
    if (!confirm("Are you sure you want to delete this note?")) return;

    try {
        const res = await fetch(`/api/notes/${id}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Delete failed");
        fetchNotes();
    } catch (err) {
        alert(err.message);
    }
}

function escapeHtml(str) {
    return str.replace(/[&<>"']/g, (m) => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[m]));
}
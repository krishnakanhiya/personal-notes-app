document.addEventListener('DOMContentLoaded', () => {
  const notesGrid = document.getElementById('notesGrid');
  const saveNoteBtn = document.getElementById('saveNoteBtn');
  const noteTitle = document.getElementById('noteTitle');
  const noteContent = document.getElementById('noteContent');
  const noteUrl = document.getElementById('noteUrl');

  // Load all notes from backend
  async function fetchNotes() {
    try {
      const res = await fetch('/api/notes');
      if (!res.ok) throw new Error('Network error fetching notes');
      const notes = await res.json();
      renderNotes(notes);
    } catch (err) {
      console.error(err);
      notesGrid.innerHTML = `<p style="color:#ef4444;">Unable to load records from database.</p>`;
    }
  }

  // Render cards to grid
  function renderNotes(notes) {
    notesGrid.innerHTML = '';
    if (notes.length === 0) {
      notesGrid.innerHTML = `<p style="color:#64748b; grid-column: 1/-1;">No notes recorded yet. Add your first note above.</p>`;
      return;
    }

    notes.forEach(note => {
      const card = document.createElement('div');
      card.className = 'note-card';

      const urlBadge = note.url 
        ? `<a href="${note.url}" target="_blank" rel="noopener noreferrer" class="note-url">🔗 Reference Link</a>` 
        : '';

      card.innerHTML = `
        <div>
          <div class="note-title">${escapeHtml(note.title)}</div>
          <div class="note-content">${escapeHtml(note.content)}</div>
          ${urlBadge}
        </div>
        <div class="card-actions">
          <a href="/edit/${note.id}" class="btn-action">Edit</a>
          <button class="btn-action btn-delete" data-id="${note.id}">Delete</button>
        </div>
      `;

      card.querySelector('.btn-delete').addEventListener('click', () => deleteNote(note.id));
      notesGrid.appendChild(card);
    });
  }

  // Create new note
  saveNoteBtn.addEventListener('click', async () => {
    const title = noteTitle.value.trim();
    const content = noteContent.value.trim();
    const url = noteUrl.value.trim();

    if (!title || !content) {
      alert('Please fill out both the title and content fields.');
      return;
    }

    try {
      const res = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, url })
      });

      if (res.ok) {
        noteTitle.value = '';
        noteContent.value = '';
        noteUrl.value = '';
        fetchNotes();
      } else {
        alert('Database save failed. Check server logs.');
      }
    } catch (err) {
      console.error(err);
      alert('Server communication error.');
    }
  });

  // Delete note
  async function deleteNote(id) {
    if (!confirm('Are you sure you want to delete this note?')) return;

    try {
      const res = await fetch(`/api/notes/${id}`, { method: 'DELETE' });
      if (res.ok) {
        fetchNotes();
      } else {
        alert('Could not delete note.');
      }
    } catch (err) {
      console.error(err);
    }
  }

  // Prevent XSS injection in notes
  function escapeHtml(str) {
    const div = document.createElement('div');
    div.innerText = str;
    return div.innerHTML;
  }

  // Initial fetch
  fetchNotes();
});
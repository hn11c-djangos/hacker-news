function confirmDelete(event) {
    if (!confirm("Are you sure you want to delete this submission?")) {
        event.preventDefault();
    }
}

function showLoginPrompt() {
    alert("Please log in to access .");
}

function showUpdateSuccess() {
    if (document.querySelector('.errorlist')) {
        alert("Profile update failed. Please check the form for errors.");
    } else {
        alert("Profile updated successfully!");
    }
}
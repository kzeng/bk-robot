function runTask(taskId) {
    fetch(`/api/tasks/${taskId}/run`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to run task');
        }
        return response.json();
    })
    .then(data => {
        alert(`Task ${taskId} is now running.`);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while running the task.');
    });
}
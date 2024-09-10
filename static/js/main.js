document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('waitlistForm');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const fullName = document.getElementById('fullName').value;
        const email = document.getElementById('email').value;

        try {
            const response = await fetch('/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ full_name: fullName, email: email }),
            });

            const data = await response.json();

            if (response.ok) {
                alert(data.message);
                form.reset();
            } else {
                alert(data.error || 'An error occurred. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
});

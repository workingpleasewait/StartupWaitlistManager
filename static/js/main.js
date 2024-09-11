document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('waitlistForm');
    const referralInfo = document.getElementById('referralInfo');
    const referralCodeDisplay = document.getElementById('referralCodeDisplay');
    const referralCountDisplay = document.getElementById('referralCountDisplay');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const fullName = document.getElementById('fullName').value;
        const email = document.getElementById('email').value;
        const referralCode = document.getElementById('referralCode').value;

        try {
            const response = await fetch('/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ full_name: fullName, email: email, referral_code: referralCode }),
            });

            const data = await response.json();

            if (response.ok) {
                alert(data.message);
                form.reset();
                
                // Display referral information
                referralCodeDisplay.textContent = data.referral_code;
                referralInfo.classList.remove('hidden');

                // Fetch and display referral stats
                fetchReferralStats(data.referral_code);
            } else {
                alert(data.error || 'An error occurred. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });

    async function fetchReferralStats(referralCode) {
        try {
            const response = await fetch(`/referral_stats/${referralCode}`);
            const data = await response.json();

            if (response.ok) {
                referralCountDisplay.textContent = `You have referred ${data.referral_count} people.`;
            } else {
                console.error('Error fetching referral stats:', data.error);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }
});

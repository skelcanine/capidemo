// Client-Side Timezone Conversion & UI Helper Logic

document.addEventListener("DOMContentLoaded", function() {
    convertUtcToLocalTime();
});

function convertUtcToLocalTime() {
    const timeElements = document.querySelectorAll('[data-utc]');
    
    timeElements.forEach(elem => {
        const utcStr = elem.getAttribute('data-utc');
        if (!utcStr) return;

        try {
            // Parse UTC timestamp string
            const utcDate = new Date(utcStr.endsWith('Z') ? utcStr : utcStr + 'Z');
            if (isNaN(utcDate.getTime())) return;

            // Detect user local timezone offset
            const offsetMinutes = -utcDate.getTimezoneOffset();
            const offsetHours = Math.floor(Math.abs(offsetMinutes) / 60);
            const remainingMins = Math.abs(offsetMinutes) % 60;
            
            let tzTag = "UTC";
            if (offsetMinutes > 0) {
                tzTag = `UTC+${offsetHours}${remainingMins > 0 ? ':' + remainingMins : ''}`;
            } else if (offsetMinutes < 0) {
                tzTag = `UTC-${offsetHours}${remainingMins > 0 ? ':' + remainingMins : ''}`;
            }

            // Format date locally
            const options = {
                day: '2-digit',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: elem.hasAttribute('data-show-seconds') ? '2-digit' : undefined,
                hour12: false
            };

            const formatter = new Intl.DateTimeFormat(navigator.language || 'en-US', options);
            const localFormatted = formatter.format(utcDate);

            // Set formatted local text with explicit timezone offset tag (e.g. "01 Oct 2026, 00:45 UTC+3")
            elem.innerText = `${localFormatted} ${tzTag}`;
        } catch (e) {
            // Fallback: keep original text
            console.log("Timezone conversion fallback:", e);
        }
    });
}

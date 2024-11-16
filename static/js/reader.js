class TextReader {
    constructor() {
        this.currentSection = -1;
        this.sections = Array.from(document.querySelectorAll('.text-section'));
        this.speed = 5;
        this.isPaused = true;
        this.setupControls();
        this.setupKeyboardControls();
    }

    setupControls() {
        // Navigation buttons
        this.prevBtn = document.getElementById('prev-btn');
        this.nextBtn = document.getElementById('next-btn');
        this.prevBtn.addEventListener('click', () => this.previousSection());
        this.nextBtn.addEventListener('click', () => this.nextSection());

        // Speed control
        this.speedControl = document.getElementById('speed-control');
        this.speedControl.addEventListener('input', (e) => {
            this.speed = parseInt(e.target.value);
        });

        // Command input
        this.commandInput = document.getElementById('command-input');
        this.commandSubmit = document.getElementById('command-submit');
        
        this.commandSubmit.addEventListener('click', () => {
            const command = this.commandInput.value;
            if (commandParser.parse(command)) {
                this.commandInput.value = '';
            }
        });

        this.commandInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const command = this.commandInput.value;
                if (commandParser.parse(command)) {
                    this.commandInput.value = '';
                }
            }
        });
    }

    setupKeyboardControls() {
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.isPaused ? this.resume() : this.pause();
            }
            else if (e.code === 'ArrowRight') {
                this.nextSection();
            }
            else if (e.code === 'ArrowLeft') {
                this.previousSection();
            }
        });
    }

    start() {
        if (this.currentSection === -1) {
            this.nextSection();
        }
    }

    pause() {
        this.isPaused = true;
    }

    resume() {
        this.isPaused = false;
        if (this.currentSection === -1) {
            this.nextSection();
        }
    }

    previousSection() {
        if (this.currentSection > 0) {
            this.sections[this.currentSection].classList.remove('active');
            this.currentSection--;
            this.sections[this.currentSection].classList.add('active');
            this.updateNavigationButtons();
        }
    }

    nextSection() {
        if (this.currentSection < this.sections.length - 1) {
            if (this.currentSection >= 0) {
                this.sections[this.currentSection].classList.remove('active');
            }
            this.currentSection++;
            this.sections[this.currentSection].style.display = 'block';
            this.sections[this.currentSection].classList.add('active');
            this.updateNavigationButtons();
        }
    }

    updateNavigationButtons() {
        this.prevBtn.disabled = this.currentSection <= 0;
        this.nextBtn.disabled = this.currentSection >= this.sections.length - 1;
    }
}

// Initialize the reader when the document is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.reader = new TextReader();
});

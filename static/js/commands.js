class CommandParser {
    constructor() {
        this.commands = {
            'commencer': () => this.startReading(),
            'help': () => this.showHelp(),
            'pause': () => window.reader.pause(),
            'resume': () => window.reader.resume(),
            'skip': () => window.reader.nextSection()
        };
    }

    parse(input) {
        const command = input.toLowerCase().trim();
        if (this.commands[command]) {
            this.commands[command]();
            return true;
        }
        return false;
    }

    startReading() {
        window.reader.start();
    }

    showHelp() {
        alert(`Available commands:
        - commencer: Start reading
        - pause: Pause reading
        - resume: Resume reading
        - skip: Skip to next section
        - help: Show this help message`);
    }
}

const commandParser = new CommandParser();

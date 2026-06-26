const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Source and target directories
const sourceDir = path.join(__dirname, '..', 'frontend', 'dist');
const targetDir = path.join(__dirname, '..', 'build');

try {
    // Create build directory if it doesn't exist
    if (!fs.existsSync(targetDir)) {
        fs.mkdirSync(targetDir, { recursive: true });
        console.log('Created build directory');
    }

    // Copy all files and directories from frontend/dist to build/
    const files = fs.readdirSync(sourceDir);

    for (const file of files) {
        const sourcePath = path.join(sourceDir, file);
        const targetPath = path.join(targetDir, file);

        const stat = fs.statSync(sourcePath);

        if (stat.isDirectory()) {
            // Copy directory recursively
            execSync(`xcopy "${sourcePath}" "${targetPath}" /E /I /Y`, { stdio: 'inherit' });
        } else {
            // Copy file
            fs.copyFileSync(sourcePath, targetPath);
            console.log(`Copied: ${file}`);
        }
    }

    console.log('Build directory setup complete!');
} catch (error) {
    console.error('Error setting up build directory:', error);
    process.exit(1);
}
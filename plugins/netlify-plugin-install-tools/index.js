module.exports = {
    onPreBuild: async ({ utils }) => {
        const { run, build } = utils;

        console.log("=== Installing build tools (mise, just, uv) ===");

        try {
            // Check if mise is already installed (cached)
            const miseExists = await run.command(
                'command -v mise || echo "not-found"',
                {
                    reject: false,
                },
            );

            if (miseExists.stdout.includes("not-found")) {
                console.log("Installing mise...");
                await run.command("curl https://mise.run | sh");

                // Add mise to PATH for subsequent commands
                process.env.PATH = `${process.env.HOME}/.local/bin:${process.env.PATH}`;
            } else {
                console.log("mise already installed (cached)");
            }

            // Trust the mise configuration in this repo
            await run.command("mise trust");

            // Install tools from mise.toml
            console.log("Installing tools from mise.toml...");
            await run.command("mise install");

            // Install just and uv explicitly (latest versions)
            console.log("Installing just and uv...");
            await run.command("mise use just@latest");
            await run.command("mise use uv@latest");

            // Activate mise environment for the build
            // This ensures just/uv are available in PATH
            await run.command("mise activate bash");

            // Update PATH for the rest of the build
            const miseBinDir = `${process.env.HOME}/.local/share/mise/shims`;
            process.env.PATH = `${miseBinDir}:${process.env.PATH}`;

            console.log("✓ Build tools installed successfully");
        } catch (error) {
            // Fail the build if tool installation fails
            build.failBuild("Failed to install build tools", { error });
        }
    },
};

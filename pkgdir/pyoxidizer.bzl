def make_exe():
    dist = default_python_distribution()
    policy = dist.make_python_packaging_policy()
    python_config = dist.make_python_interpreter_config()
    python_config.run_command = "from diskpatrol.cli import main; main()"
    exe = dist.to_python_executable(
        name="diskpatrol",
        packaging_policy=policy,
        config=python_config,
    )
    exe.add_python_resources(exe.pip_install([CWD]))

    return exe

def make_install(exe):
    files = FileManifest()
    files.add_python_resource(".", exe)

    return files

register_target("exe", make_exe)
resolve_targets()

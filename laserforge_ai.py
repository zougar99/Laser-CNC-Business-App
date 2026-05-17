#!/usr/bin/env python3
"""
LaserForge AI - Unified Laser Cutting & Plotting Platform
Custom Edition for werlist99

Combines LaserCore Engine and GRBL-Plotter features with AI capabilities.
"""

import argparse
import os.path
import sys

APPLICATION_NAME = "LaserForge AI - werlist99 Edition"
APPLICATION_VERSION = "1.0.0"
APPLICATION_AUTHOR = "werlist99"

if not getattr(sys, "frozen", False):
    if os.path.isdir(os.path.join(sys.path[0], ".git")):
        APPLICATION_VERSION += " git"
    elif os.path.isdir(os.path.join(sys.path[0], ".github")):
        APPLICATION_VERSION += " src"
    else:
        APPLICATION_VERSION += " pkg"


def pair(value):
    """Parse key=value pairs."""
    rv = value.split("=")
    if len(rv) != 2:
        pass
    return rv


parser = argparse.ArgumentParser(
    description="LaserForge AI - Unified Laser Cutting & Plotting Platform"
)
parser.add_argument("-V", "--version", action="store_true", help="Show version")
parser.add_argument("input", nargs="?", type=argparse.FileType("r"), help="Input file")
parser.add_argument("-o", "--output", type=argparse.FileType("w"), help="Output file")
parser.add_argument("-z", "--no-gui", action="store_true", help="Run without GUI")
parser.add_argument(
    "-Z", "--gui-suppress", action="store_true", help="Completely suppress GUI"
)
parser.add_argument(
    "-w", "--simpleui", action="store_true", help="Use simple UI"
)
parser.add_argument(
    "-b", "--batch", type=argparse.FileType("r"), help="Console batch file"
)
parser.add_argument("-c", "--console", action="store_true", help="Start as console")
parser.add_argument(
    "-e",
    "--execute",
    action="append",
    type=str,
    nargs="?",
    help="Execute console command",
)
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose debugging")
parser.add_argument(
    "-q", "--quit", action="store_true", help="Quit on spooler complete"
)
parser.add_argument("-a", "--auto", action="store_true", help="Start running laser")
parser.add_argument(
    "-s",
    "--set",
    action="append",
    nargs="?",
    type=pair,
    metavar="key=value",
    help="Set a device variable",
)
parser.add_argument(
    "-P", "--profile", type=int, default=None, help="Specify settings profile index"
)
parser.add_argument(
    "-p",
    "--no-plugins",
    action="store_true",
    help="Do not load plugins",
)
parser.add_argument(
    "-A",
    "--disable-ansi",
    action="store_true",
    default=False,
    help="Disable ANSI colors",
)
parser.add_argument(
    "-X",
    "--nuke-settings",
    action="store_true",
    default=False,
    help="Don't load config file at startup",
)
parser.add_argument(
    "-L",
    "--language",
    type=str,
    default=None,
    help="Force default language",
)
parser.add_argument(
    "-f",
    "--profiler",
    type=str,
    default=None,
    help="Run with profiler file specified",
)
parser.add_argument(
    "-u",
    "--lock-device-config",
    action="store_true",
    help="Lock device config from editing",
)
parser.add_argument(
    "-U",
    "--lock-general-config",
    action="store_true",
    help="Lock general config from editing",
)
parser.add_argument(
    "-m",
    "--minimized",
    action="store_true",
    help="Start window minimized",
)
parser.add_argument(
    "-M",
    "--maximized",
    action="store_true",
    help="Start window maximized",
)
parser.add_argument(
    "-d", "--daemon", action="store_true", help="Keep LaserForge AI in background"
)
parser.add_argument(
    "--ai-enabled",
    action="store_true",
    default=True,
    help="Enable AI features (default: True)",
)
parser.add_argument(
    "--ai-model",
    type=str,
    default="default",
    help="AI model to use (default, fast, accurate)",
)


def run():
    """Main entry point."""
    argv = sys.argv[1:]
    args = parser.parse_args(argv)

    if args.version:
        print(f"{APPLICATION_NAME} {APPLICATION_VERSION}")
        return

    python_version_required = (3, 6)
    if sys.version_info < python_version_required:
        print(
            f"{APPLICATION_NAME} {APPLICATION_VERSION} requires Python "
            f"{python_version_required[0]}.{python_version_required[1]} or greater."
        )
        return

    if args.profiler:
        import cProfile

        profiler = cProfile.Profile()
        profiler.enable()
        _run = _exe(False, args)
        while _run:
            _run = _exe(True, args)
            if "nuke_settings" in args:
                args.nuke_settings = False
        profiler.disable()
        profiler.dump_stats(args.profiler)
        return

    _run = _exe(False, args)
    # Don't loop if GUI is running - MainLoop will block
    if _run:
        while _run:
            if "nuke_settings" in args:
                args.nuke_settings = False
            _run = _exe(True, args)


def _exe(restarted, args):
    """Execute the application."""
    # Import core modules
    try:
        from laserforge_ai.core.kernel import Kernel
        from laserforge_ai.core.plugins import load_plugins
        
        # Use unified LaserForge AI kernel
        kernel = Kernel(
            APPLICATION_NAME,
            APPLICATION_VERSION,
            APPLICATION_NAME,
            ansi=not args.disable_ansi,
            ignore_settings=args.nuke_settings,
            restarted=restarted,
            ai_enabled=args.ai_enabled,
            ai_model=args.ai_model,
        )
        kernel.args = args
        
        # Load plugins
        plugins = load_plugins()
        for plugin in plugins:
            if plugin:
                try:
                    kernel.add_plugin(plugin)
                except Exception as e:
                    logger = __import__('logging').getLogger(__name__)
                    logger.warning("Could not add plugin: {}".format(e))
        
    except ImportError as e:
        # Fallback: try to use LaserCore Engine directly if integration not complete
        print("Warning: Using LaserCore Engine fallback mode")
        try:
            from meerk40t.kernel import Kernel
            from meerk40t.external_plugins import plugin as external_plugins
            from meerk40t.internal_plugins import plugin as internal_plugins

            kernel = Kernel(
                APPLICATION_NAME,
                APPLICATION_VERSION,
                APPLICATION_NAME,
                ansi=not args.disable_ansi,
                ignore_settings=args.nuke_settings,
                restarted=restarted,
            )
            kernel.args = args
            kernel.add_plugin(internal_plugins)
            kernel.add_plugin(external_plugins)
        except ImportError:
            print("LaserCore Engine (meerk40t) not found. Running in standalone GUI mode.")
            # Create minimal kernel for GUI only
            from laserforge_ai.core.kernel import Kernel
            kernel = Kernel(
                APPLICATION_NAME,
                APPLICATION_VERSION,
                APPLICATION_NAME,
                ansi=not args.disable_ansi,
                ignore_settings=args.nuke_settings,
                restarted=restarted,
                ai_enabled=args.ai_enabled,
                ai_model=args.ai_model,
            )
            kernel.args = args

    auto = hasattr(kernel.args, "auto") and kernel.args.auto
    command = hasattr(kernel.args, "execute") and kernel.args.execute
    console = hasattr(kernel.args, "console") and kernel.args.console
    daemon = hasattr(kernel.args, "daemon") and kernel.args.daemon

    server_mode = False
    if command:
        for c in command:
            server_mode = server_mode or any(
                substring in c
                for substring in (
                    "lhyserver",
                    "grblserver",
                    "ruidacontrol",
                    "grblcontrol",
                    "webserver",
                )
            )

    nogui = (hasattr(kernel.args, "gui_suppress") and kernel.args.gui_suppress) or (
        hasattr(kernel.args, "no_gui") and kernel.args.no_gui
    )

    require_partial_mode = False
    if (not console or nogui) and (auto or daemon or server_mode):
        require_partial_mode = True

    # Execute kernel - if it returns False, try to start GUI anyway
    result = kernel(partial=require_partial_mode)
    
    # Check if GUI was started by plugins
    if hasattr(kernel, 'gui_app') and kernel.gui_app:
        # GUI is already running, MainLoop will block
        # Don't return anything, let MainLoop handle it
        return False
    
    # If kernel execution returned False but GUI is requested, start GUI directly
    if not result and not nogui and not console:
        try:
            import wx
            from laserforge_ai.gui.main_window import MainWindow
            
            print("Starting GUI directly...")
            app = wx.App(False)
            main_window = MainWindow(None, kernel, "LaserForge AI - werlist99 Edition")
            main_window.Show()
            print("GUI window created and shown")
            app.MainLoop()
            return False
        except Exception as e:
            print("Error starting GUI: {}".format(e))
            import traceback
            traceback.print_exc()
            return False
    
    return hasattr(kernel, "restart") and kernel.restart


if __name__ == "__main__":
    run()

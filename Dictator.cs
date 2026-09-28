using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Windows.Forms;
[assembly: AssemblyTitle("Dictatoro")]
[assembly: AssemblyProduct("Dictatoro")]
[assembly: AssemblyVersion("0.3.0.0")]
[assembly: AssemblyFileVersion("0.3.0.0")]
static class Entry {
    [STAThread]
    static int Main(string[] args) {
        try {
            string folder = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            string mode = Array.IndexOf(args, "--startup") >= 0 ? " --startup" : "";
            bool test = Array.IndexOf(args, "--self-test") >= 0;
            if (test) mode = " --self-test";
            var info = new ProcessStartInfo(Path.Combine(folder, "runtime", "pythonw.exe"));
            info.Arguments = "-B \"" + Path.Combine(folder, "launcher.py") + "\"" + mode;
            info.WorkingDirectory = folder;
            info.UseShellExecute = false;
            info.CreateNoWindow = true;
            using (var process = Process.Start(info)) {
                if (test) { process.WaitForExit(); return process.ExitCode; }
            }
            return 0;
        } catch (Exception error) {
            MessageBox.Show("Dictatoro 0.3\n\n" + error.Message, "Dictatoro", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }
}

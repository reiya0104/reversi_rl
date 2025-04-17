use pyo3_build_config::add_extension_module_link_args;
use std::env;

fn main() {
    add_extension_module_link_args();

    // Pythonのライブラリパスを取得
    let python_root = env::var("PYTHON_ROOT").unwrap_or_else(|_| {
        let output = std::process::Command::new("python3-config")
            .arg("--prefix")
            .output()
            .expect("Failed to execute python3-config");
        String::from_utf8(output.stdout).unwrap().trim().to_string()
    });

    // ライブラリパスを設定
    println!("cargo:rustc-link-search=native={}/lib", python_root);
    println!("cargo:rustc-link-lib=dylib=python3.12");
}

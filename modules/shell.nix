{ inputs, ... }: {
  imports = [ inputs.devshell.flakeModule ];

  perSystem = { config, pkgs, ... }: {
    devshells.default = {
      packages = with pkgs; [
        cargo
        rustc
        openssl
        pkg-config
        (python3.withPackages (p: with p; [ gitpython multiprocess ]))
        config.treefmt.build.wrapper
      ];
      commands = [
        {
          name = "deploy";
          help = "Render pages for deployment";
          command = ''
            mkdir -p ~/.local/state/zhf
            ln -sf ~/.local/state/zhf data
            rm -rf public
            ./scripts/render-page.sh master public
            ./scripts/render-page.sh release-26.05 public/release-26.05
          '';
        }
      ];
    };
  };
}

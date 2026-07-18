{ inputs, ... }: {
  imports = [ inputs.devshell.flakeModule ];

  perSystem = { config, pkgs, ... }: {
    devshells.default = {
      packages = with pkgs; [
        cargo
        rustc
        openssl
        pkg-config
        python3
        python3Packages.gitpython
        python3Packages.multiprocess
        config.treefmt.build.wrapper
      ];
      commands = [
        {
          name = "deploy";
          help = "Render pages for deployment";
          command = ''
            ln -sf /var/lib/zhf data
            rm -rf public
            ./scripts/render-page.sh master public
            ./scripts/render-page.sh release-26.05 public/release-26.05
          '';
        }
      ];
    };
  };
}

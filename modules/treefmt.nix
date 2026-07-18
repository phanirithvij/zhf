{ inputs, config, ... }: {
  imports = [ inputs.treefmt-nix.flakeModule ];

  perSystem = { pkgs, ... }: {
    treefmt.config = {
      projectRootFile = "flake.nix";
      programs.rustfmt.enable = true;
      programs.black.enable = true;
      programs.shfmt.enable = true;
      programs.prettier = {
        enable = true;
        includes = ["*.html" "*.css" "*.yml" "*.yaml" "*.json"];
      };
    };
  };
}

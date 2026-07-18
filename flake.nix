{
  outputs = inputs: inputs.flake-parts.lib.mkFlake { inherit inputs; } (inputs.import-tree ./modules);
  inputs = {
    devshell.url = "github:numtide/devshell/main";
    flake-parts.url = "github:hercules-ci/flake-parts/main";
    import-tree.url = "github:denful/import-tree/main";
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    treefmt-nix = {
      url = "github:numtide/treefmt-nix/main";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
}

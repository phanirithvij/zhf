{
  perSystem = { pkgs, ... }: {
    packages.default = pkgs.rustPlatform.buildRustPackage {
      pname = "zhf";
      version = "0.1.0";
      src = ../.;
      cargoLock = {
        lockFile = ../Cargo.lock;
      };
      nativeBuildInputs = [ pkgs.pkg-config pkgs.makeWrapper ];
      buildInputs = [ pkgs.openssl ];
      # disable tests during build, it just needs to build
      doCheck = false;

      postInstall = ''
        cp -r scripts $out/scripts
        # create wrappers for the python scripts
        for script in fetch-maintainers.py filter-maintainers.py; do
          wrapProgram $out/scripts/$script \
            --prefix PATH : ${pkgs.lib.makeBinPath [ pkgs.python3 pkgs.python3Packages.gitpython pkgs.python3Packages.multiprocess ]}
          ln -s $out/scripts/$script $out/bin/$script
        done
        wrapProgram $out/scripts/render-page.sh \
          --prefix PATH : $out/bin
        ln -s $out/scripts/render-page.sh $out/bin/render-page.sh
      '';
    };
  };
}

{
  perSystem =
    { pkgs, ... }:
    {
      treefmt = {
        projectRootFile = "flake.nix";
        enableDefaultExcludes = true;
        programs = {
          hclfmt.enable = true;
          nixfmt.enable = true;
          prettier.enable = true;
          ruff-format.enable = true;
          shfmt.enable = true;
          statix.enable = true;
          taplo.enable = true;
          terraform.enable = true;
        };
        settings.global.excludes = [
          "*.terraform.lock.hcl"
          "LICENSE"
        ];
      };
      devenv.shells.default = {
        containers = pkgs.lib.mkForce { };
        languages = {
          opentofu.enable = true;
          nix.enable = true;
        };
        languages.python = {
          enable = true;
          uv.enable = true;
        };
        cachix = {
          enable = true;
          push = "shikanime";
        };
        git-hooks.hooks = {
          actionlint.enable = true;
          deadnix.enable = true;
          flake-checker.enable = true;
          shellcheck.enable = true;
          tflint.enable = true;
        };
        packages = [
          pkgs.gh
          pkgs.skaffold
          pkgs.uv
        ];
      };
    };
}

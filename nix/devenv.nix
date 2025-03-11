{
  perSystem =
    { pkgs, ... }:
    let
      google-cloud-sdk = pkgs.google-cloud-sdk.withExtraComponents [
        pkgs.google-cloud-sdk.components.alpha
        pkgs.google-cloud-sdk.components.beta
        pkgs.google-cloud-sdk.components.cloud-run-proxy
        pkgs.google-cloud-sdk.components.log-streaming
      ];
    in
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
          uv = {
            enable = true;
            sync.enable = true;
          };
        };
        cachix = {
          enable = true;
          push = "shikanime";
        };
        git-hooks.hooks = {
          actionlint.enable = true;
          deadnix.enable = true;
          flake-checker.enable = true;
          hadolint.enable = true;
          shellcheck.enable = true;
          tflint.enable = true;
        };
        packages = [
          google-cloud-sdk
          pkgs.gh
          pkgs.kubectl
          pkgs.kustomize
          pkgs.skaffold
          pkgs.uv
          pkgs.yq
        ];
      };
    };
}

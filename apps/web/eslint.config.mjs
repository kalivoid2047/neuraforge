// eslint-config-next ships native flat config since v16 (dist/core-web-vitals.js
// and dist/typescript.js each `module.exports` a plain array of flat-config
// objects) -- so this no longer goes through @eslint/eslintrc's FlatCompat.
//
// That change is not cosmetic: FlatCompat re-validates whatever it loads
// against the OLD .eslintrc JSON schema (see @eslint/eslintrc/lib/shared/
// config-validator.js). Flat-config-native plugins intentionally contain
// circular references (a plugin's `configs.flat` object referencing the
// plugin object that defines it), which that legacy JSON-shaped validator
// cannot serialize -- it throws "Converting circular structure to JSON".
// Importing the flat configs directly avoids the incompatible layer instead
// of working around what it produces.
import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

const eslintConfig = [
  { ignores: [".next/**", "node_modules/**", "next-env.d.ts"] },
  ...nextCoreWebVitals,
  ...nextTypescript,
];

export default eslintConfig;

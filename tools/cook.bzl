"""A rule that renders a .cook file's outputs as two independent actions.

The .tex output is split into its own action (and binary, see
cook_gen_tex.py) from the .html/manifest outputs (cook_gen_html.py) so that
html-only changes don't invalidate the tex action -- the downstream
LaTeX/PDF build is slow, so it shouldn't rebuild just because the HTML
renderer changed, and vice versa.
"""

def _cook_recipe_impl(ctx):
    name = ctx.file.cook.basename
    if name.endswith(".cook"):
        name = name[:-len(".cook")]

    tex = ctx.actions.declare_file("recipes/" + name + ".tex")
    html = ctx.actions.declare_file(name + "/index.html")
    manifest = ctx.actions.declare_file(name + ".json")

    tex_args = ctx.actions.args()
    tex_args.add("--input=%s" % ctx.file.cook.path)
    tex_args.add("--tex=%s" % tex.path)

    ctx.actions.run(
        executable = ctx.executable._cook_gen_tex,
        arguments = [tex_args],
        inputs = [ctx.file.cook],
        outputs = [tex],
        mnemonic = "CookGenTex",
        progress_message = "Rendering recipe tex for %{input}",
    )

    html_args = ctx.actions.args()
    html_args.add("--input=%s" % ctx.file.cook.path)
    html_args.add("--html=%s" % html.path)
    html_args.add("--manifest=%s" % manifest.path)

    ctx.actions.run(
        executable = ctx.executable._cook_gen_html,
        arguments = [html_args],
        inputs = [ctx.file.cook],
        outputs = [html, manifest],
        mnemonic = "CookGenHtml",
        progress_message = "Rendering recipe html for %{input}",
    )

    return [
        DefaultInfo(files = depset([tex, html, manifest])),
        OutputGroupInfo(
            tex = depset([tex]),
            html = depset([html]),
            manifest = depset([manifest]),
        ),
    ]

cook_recipe = rule(
    implementation = _cook_recipe_impl,
    attrs = {
        "cook": attr.label(allow_single_file = [".cook"], mandatory = True),
        "_cook_gen_tex": attr.label(
            default = Label("//tools:cook_gen_tex"),
            executable = True,
            cfg = "exec",
        ),
        "_cook_gen_html": attr.label(
            default = Label("//tools:cook_gen_html"),
            executable = True,
            cfg = "exec",
        ),
    },
    doc = """Renders a .cook file to .tex, .html, and a JSON manifest.

    Runs as two actions (tex; html+manifest) so a change to one renderer
    doesn't invalidate the other's action.
    """,
)

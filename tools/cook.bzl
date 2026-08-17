"""A rule that renders all outputs from one .cook file in a single action."""

def _cook_recipe_impl(ctx):
    name = ctx.file.cook.basename
    if name.endswith(".cook"):
        name = name[:-len(".cook")]

    tex = ctx.actions.declare_file("recipes/" + name + ".tex")
    html = ctx.actions.declare_file(name + "/index.html")
    manifest = ctx.actions.declare_file(name + ".json")

    args = ctx.actions.args()
    args.add("--input=%s" % ctx.file.cook.path)
    args.add("--tex=%s" % tex.path)
    args.add("--html=%s" % html.path)
    args.add("--manifest=%s" % manifest.path)

    ctx.actions.run(
        executable = ctx.executable._cook_gen,
        arguments = [args],
        inputs = [ctx.file.cook],
        outputs = [tex, html, manifest],
        mnemonic = "CookGen",
        progress_message = "Rendering recipe outputs for %{input}",
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
        "_cook_gen": attr.label(
            default = Label("//tools:cook_gen"),
            executable = True,
            cfg = "exec",
        ),
    },
    doc = """Renders a .cook file to .tex, .html, and a JSON manifest.

    One action parses the .cook file once and writes all three outputs,
    instead of running a separate tool invocation per output format.
    """,
)

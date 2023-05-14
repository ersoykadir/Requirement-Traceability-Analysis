import jinja2
import pdfkit

def create_pdf(graph):
    requirements = graph.requirement_nodes.values()
    issues = graph.issue_nodes.values()
    prs = graph.pr_nodes.values()
    #requirements = [{'number':'11.1.1', 'description':"Users shall get the fuck out", 'number_of_connected_issues': 65, 'number_of_connected_prs':10}]
    context = {'requirements': requirements, 'issues':issues, 'prs':prs}

    template_loader = jinja2.FileSystemLoader('.\\')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("dashboard_pdf_html.html")
    output_text = template.render(context)

    config = pdfkit.configuration(wkhtmltopdf='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe')
    pdfkit.from_string(output_text, 'pdf_generated.pdf', configuration=config)

#create_pdf("cee")
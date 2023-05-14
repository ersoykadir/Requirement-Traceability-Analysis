import jinja2
import pdfkit

def create_pdf(graph):
    requirements = graph.requirement_nodes.values()
    avg = 0
    zero_link_reqs = []
    for i in requirements:
        avg = avg + i.number_of_connected_issues +  i.number_of_connected_prs
        if i.number_of_connected_prs == 0 and i.number_of_connected_issues == 0:
            zero_link_reqs.append(i.number)
    avg = round(avg / len(requirements))
    issues = graph.issue_nodes.values()
    prs = graph.pr_nodes.values()
    #requirements = [{'number':'11.1.1', 'description':"Users shall get the fuck out", 'number_of_connected_issues': 65, 'number_of_connected_prs':10}]
    context = {'requirements': requirements, 'issues':issues, 'prs':prs, 'avg':avg, 'zero_link_reqs':zero_link_reqs}

    template_loader = jinja2.FileSystemLoader('.\\')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("dashboard_pdf_html.html")
    output_text = template.render(context)

    config = pdfkit.configuration(wkhtmltopdf='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe')
    pdfkit.from_string(output_text, 'pdf_generated.pdf', configuration=config)

#create_pdf("cee")
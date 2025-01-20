from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import pandas as pd
import os
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

class DataHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            try:
                # Read Excel file
                df = pd.read_excel('JGP.xlsx')
                
                # Convert datetime columns to string format
                for column in df.select_dtypes(include=['datetime64[ns]']).columns:
                    df[column] = df[column].dt.strftime('%Y-%m-%d')
                
                # Convert to records and handle NaN values
                data = df.where(pd.notna(df), None).to_dict('records')
                
                # Print data to terminal for monitoring
                print(f"Total records loaded: {len(data)}")
                if len(data) > 0:
                    print("Sample record:", json.dumps(data[0], indent=2, cls=DateTimeEncoder))

                # Read the HTML template
                with open('index.html', 'r', encoding='utf-8') as f:
                    html_content = f.read()

                # Create the data script tag with the Excel data
                data_script = f"""
                <script>
                    // Excel data embedded directly
                    const excelData = {json.dumps(data, cls=DateTimeEncoder)};
                    
                    // Initialize UI elements
                    const countySelect = document.getElementById('county');
                    const searchButton = document.getElementById('searchButton');
                    const resultsDiv = document.getElementById('results');
                    const loadingDiv = document.getElementById('loading');
                    const statusSection = document.getElementById('statusSection');

                    // Setup on page load
                    window.addEventListener('load', () => {{
                        try {{
                            // Extract unique counties
                            const counties = [...new Set(excelData
                                .map(row => row.County)
                                .filter(Boolean)
                                .map(county => county.trim())
                            )].sort();

                            // Populate county dropdown
                            countySelect.innerHTML = '<option value="">Choose a county...</option>' +
                                counties.map(county => 
                                    `<option value="${{county}}">${{county}}</option>`
                                ).join('');

                            // Enable controls
                            countySelect.disabled = false;
                            searchButton.disabled = false;

                            // Show success status
                            statusSection.innerHTML = `
                                <div class="status-icon" style="color: var(--success-color);">
                                    <i class="fas fa-check-circle"></i>
                                </div>
                                <div class="status-text" style="color: var(--success-color);">
                                    Data loaded successfully!
                                </div>
                                <div class="helper-text">${{excelData.length}} records found</div>
                            `;
                        }} catch (error) {{
                            console.error('Error:', error);
                            statusSection.innerHTML = `
                                <div class="status-icon" style="color: #ef4444;">
                                    <i class="fas fa-exclamation-circle"></i>
                                </div>
                                <div class="status-text" style="color: #ef4444;">
                                    Could not load data
                                </div>
                                <div class="helper-text">Error processing data</div>
                            `;
                        }}
                    }});

                    // Search button click handler
                    searchButton.addEventListener('click', () => {{
                        const county = countySelect.value;
                        const idNumber = document.getElementById('idNumber').value.trim();
                        const phoneNumber = document.getElementById('phoneNumber').value.trim();
                        const fullName = document.getElementById('fullName').value.trim();

                        if (!county) {{
                            alert('Please select a county first');
                            return;
                        }}

                        loadingDiv.style.display = 'block';
                        resultsDiv.innerHTML = '';

                        // Filter the data
                        let results = excelData.filter(row => 
                            row.County && row.County.toLowerCase() === county.toLowerCase()
                        );

                        if (idNumber) {{
                            results = results.filter(row => 
                                String(row['WHAT IS YOUR NATIONAL ID?']).includes(idNumber)
                            );
                        }}

                        if (phoneNumber) {{
                            results = results.filter(row => 
                                String(row['Phone Number']).includes(phoneNumber)
                            );
                        }}

                        if (fullName) {{
                            results = results.filter(row => 
                                row['Full Name'] && 
                                row['Full Name'].toLowerCase().includes(fullName.toLowerCase())
                            );
                        }}

                        // Display results
                        setTimeout(() => {{
                            loadingDiv.style.display = 'none';

                            if (results.length === 0) {{
                                resultsDiv.innerHTML = `
                                    <div class="no-results">
                                        <i class="fas fa-search" style="font-size: 48px; color: #cbd5e1; margin-bottom: 20px;"></i>
                                        <p>No matching records found. Try adjusting your search criteria.</p>
                                    </div>
                                `;
                            }} else {{
                                const tableHTML = `
                                    <div class="table-wrapper">
                                       <table>
                                            <thead>
                                                <tr>
                                                    <th>County</th>
                                                    <th>First Name</th>
                                                    <th>Last Name</th>
                                                    <th>Email Address</th>
                                                    <th>ID Number</th>
                                                    <th>Alien ID</th>
                                                    <th>Phone Number</th>
                                                    <th>Gender</th>
                                                    <th>Industry Sector</th>
                                                    <th>Age</th>
                                                    <th>Timestamp</th>
                                                    <th>Consent</th>
                                                    <th>Citizenship Status</th>
                                                    <th>Passport Number</th>
                                                    <th>Business Registration</th>
                                                    <th>Registration Number</th>
                                                    <th>Agriculture Subsector</th>
                                                    <th>Monthly Revenue (Good)</th>
                                                    <th>Monthly Revenue (Bad)</th>
                                                    <th>Regular Employees</th>
                                                    <th>Youth Regular Employees</th>
                                                    <th>Casual Employees</th>
                                                    <th>Youth Casual Employees</th>
                                                    <th>Business Records</th>
                                                    <th>Technical Assistance Needs</th>
                                                    <th>Disability Status</th>
                                                    <th>Disability Type</th>
                                                    <th>Learning Style</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${{results.map(row => `
                                                    <tr>
                                                        <td>${{row['County'] || ''}}</td>
                                                        <td>${{row['First Name'] || ''}}</td>
                                                        <td>${{row['Last Name'] || ''}}</td>
                                                        <td>${{row['Email Address'] || ''}}</td>
                                                        <td>${{row['WHAT IS YOUR NATIONAL ID?'] || ''}}</td>
                                                        <td>${{row['Alien ID'] || ''}}</td>
                                                        <td>${{row['Phone Number'] || ''}}</td>
                                                        <td>${{row['Gender'] || ''}}</td>
                                                        <td>${{row['WHAT IS THE MAIN INDUSTRY SECTOR IN WHICH YOU OPERATE IN?'] || ''}}</td>
                                                        <td>${{row['Age'] || ''}}</td>
                                                        <td>${{row['Timestamp'] || ''}}</td>
                                                        <td>${{row['I consent to answering the questions below to enable the KNCCI collect important Microdata to help track the journey of the business in the Jiinue Growth Program.'] || ''}}</td>
                                                        <td>${{row['WHAT IS YOUR CITIZENSHIP STATUS?'] || ''}}</td>
                                                        <td>${{row['PLEASE PROVIDE YOUR PASSPORT NUMBER'] || ''}}</td>
                                                        <td>${{row['IS YOUR BUSINESS REGISTERED?'] || ''}}</td>
                                                        <td>${{row['PLEASE PROVIDE YOUR REGISTRATION NUMBER'] || ''}}</td>
                                                        <td>${{row['IF AGRICULTURE, PLEASE SELECT THE MAIN SUBSECTOR'] || ''}}</td>
                                                        <td>${{row['WHAT WAS YOUR ESTIMATED MONTHLY REVENUE (KES) IN A PARTICULARLY GOOD MONTH'] || ''}}</td>
                                                        <td>${{row['WHAT WAS YOUR ESTIMATED MONTHLY REVENUE (KES) IN A PARTICULARLY BAD MONTH?'] || ''}}</td>
                                                        <td>${{row['WHAT IS THE NUMBER OF YOUR REGULAR EMPLOYEES INCLUDING BUSINESS OWNER?'] || ''}}</td>
                                                        <td>${{row['OF THESE, HOW MANY ARE YOUTH? (18 -35 YEARS OLD)'] || ''}}</td>
                                                        <td>${{row['WHAT IS THE NUMBER OF CASUAL EMPLOYEES'] || ''}}</td>
                                                        <td>${{row['OF THESE, HOW MANY ARE YOUTH? (18 -35 YEARS OLD)'] || ''}}</td>
                                                        <td>${{row['DO YOU KEEP ANY OF THE FOLLOWING RECORDS IN YOUR BUSINESS OPERATIONS? [ PLEASE SELECT ALL THAT APPLY]'] || ''}}</td>
                                                        <td>${{row['WHAT ARE THE MOST PRESSING TECHNICAL ASSISTANCE NEEDS TO IMPROVE YOUR BUSINESS OPERATIONS? [PLEASE SELECT UP TO TWO]'] || ''}}</td>
                                                        <td>${{row['DO YOU IDENTIFY AS A PERSON WITH A DISABILITY? (THIS QUESTION IS OPTIONAL AND YOUR RESPONSE WILL NOT AFFECT YOUR ELIGIBILITY FOR THE PROGRAM.)'] || ''}}</td>
                                                        <td>${{row['IF YES, PLEASE INDICATE YOUR DISABILITY'] || ''}}</td>
                                                        <td>${{row['DO YOU HAVE A PREFERRED LEARNING STYLE?'] || ''}}</td>
                                                    </tr>
                                                `).join('')}}
                                            </tbody>
                                        </table>
                                    </div>
                                    <div class="helper-text" style="margin-top: 10px;">
                                        Found ${{results.length}} matching record${{results.length === 1 ? '' : 's'}}
                                    </div>
                                `;
                                resultsDiv.innerHTML = tableHTML;
                            }}
                        }}, 100);
                    }});
                </script>
                """

                # Replace the SheetJS script tag with our data and logic
                html_content = html_content.replace('<!-- Add SheetJS -->', data_script)
                
                # Remove the original script section since we included it in data_script
                html_content = html_content.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>', '')
                
                # Serve the modified HTML
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
                
            except Exception as e:
                print(f"Error: {str(e)}")
                self.send_error(500, f"Error loading data: {str(e)}")
        else:
            # Serve any other static files
            super().do_GET()

def run_server(port=8000):
    server = HTTPServer(('localhost', port), DataHandler)
    print(f"\nServer running at http://localhost:{port}")
    print("Make sure JGP.xlsx and index.html are in the same directory")
    server.serve_forever()

if __name__ == '__main__':
    run_server()     
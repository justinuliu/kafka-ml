import { Component, OnInit } from '@angular/core';
import { Location } from '@angular/common';
import { Deployment } from '../shared/deployment.model'
import { Configuration } from '../shared/configuration.model'
import { ConfigurationService } from '../services/configuration.service';
import { DeploymentService } from '../services/deployment.service';
import { Router, ActivatedRoute } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
@Component({
  selector: 'app-deployment-view',
  templateUrl: './deployment-view.component.html',
  styleUrls: ['./deployment-view.component.css']
})
export class DeploymentViewComponent implements OnInit {

  constructor(private location: Location,
    private deploymentService: DeploymentService,
    private configurationService: ConfigurationService,
    private snackbar: MatSnackBar,
    private route: ActivatedRoute,
    private router: Router) { }

  deployment: Deployment = new Deployment();
  configuration: Configuration = new Configuration();
  configurationID: number;

  valid: boolean = false;
  detectedFrameworks: string[] = [];
  ngOnInit(): void {
    this.deployment.conf_mat_settings = false;
    if (this.route.snapshot.paramMap.has('id')) {
      this.configurationID = Number(this.route.snapshot.paramMap.get('id'));
      this.configurationService.getConfiguration(this.configurationID).subscribe(
        (data) => {
          this.configuration = <Configuration>data;
          this.valid = true;
          this.configurationService.getFrameworksUsedInConfiguration(this.configurationID).subscribe(
            (data) => {
              this.detectedFrameworks = <string[]>data
            }
          )
        },
        (err) => {
          this.snackbar.open('Configuration not found', '', {
            duration: 3000
          });
        });
    }
  }
  onSubmit(deployment: Deployment) {
    deployment.configuration = this.configurationID;

    deployment.tf_kwargs_fit = deployment.tf_kwargs_fit || "";
    deployment.tf_kwargs_val = deployment.tf_kwargs_val || "";
    deployment.pth_kwargs_fit = deployment.pth_kwargs_fit || "";

    deployment.pth_kwargs_val = deployment.pth_kwargs_val || "";

    this.deploymentService.deploy(deployment).subscribe(
      () => {
        this.router.navigateByUrl('/deployments');
      },
      (err) => {
        this.snackbar.open('Error deploying the configuration:' + (err.error), '', {
          duration: 3000
        });
      });
  }

  back() {
    this.location.back();
  }
}

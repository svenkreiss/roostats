
# MCMC Plots

This includes a comparison of the Posterior and the profile Likelihood shape in 
the middle column.<br />
![seqProp_extras](docImages/SequentialProposal_extras.png)

NLL time development with 1000 sampling points (left) and all sampling points (right).<br />
![seqProp_NLLVsTime_1000](docImages/SequentialProposal_NLLTimeDev_1000Samples.png)
![seqProp_NLLVsTime_all](docImages/SequentialProposal_NLLTimeDev_allSamples.png)

Parameter time development with 1000 sampling points (left) and all sampling points (right).<br />
![seqProp_POIVsTime_1000](docImages/SequentialProposal_POIVsTime_1000Samples.png)
![seqProp_POIVsTime_all](docImages/SequentialProposal_POIVsTime_allSamples.png)


# Sequential Proposal

Running the Standard configuration of MCMC and SequentialProposal(10.0).<br />
<!--![seqProp_interval](docImages/SequentialProposal_interval.png)-->
![seqProp_extras](docImages/SequentialProposal_POIAndFirstNuisParWalk.png)

Changing to SequentialProposal(100.0).<br />
<!--![seqProp_interval](docImages/SequentialProposal_100_interval.png)-->
![seqProp_extras](docImages/SequentialProposal_100_POIAndFirstNuisParWalk.png)

Now, using the standard SequentialProposal(10.0), let's look at various values of 
the "oversampling". This is oversampling=3.<br />
<!--![seqProp_interval](docImages/SequentialProposal_10_03_interval.png)-->
![seqProp_extras](docImages/SequentialProposal_10_03_POIAndFirstNuisParWalk.png)

And oversampling=10.<br />
<!--![seqProp_interval](docImages/SequentialProposal_10_10_interval.png)-->
![seqProp_extras](docImages/SequentialProposal_10_10_POIAndFirstNuisParWalk.png)

Work in progress.



# Batch Processing Tools

This shows a grid constructed from the parameters of interest and the bins set for 
these parameters. The algorithm is completely general and works for n parameters.
On the right, it shows the job number for every grid point for a given total number 
of jobs (in this case 16).
You can reproduce this with
```
python BatchProfileLikelihood.py --overwritePOI=SigXsecOverSM=1,alpha_syst2=0 --overwriteBins=SigXsecOverSM=6,alpha_syst2=10 -f -j 16
```
![binEnumeration](docImages/binEnumeration2D.png)


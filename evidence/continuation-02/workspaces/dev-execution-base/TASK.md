# Repair the checkpoint-2 linear execution regression

The current CLI must execute a linear pipeline and honor limit n=0 by returning zero rows. Preserve the earlier normalization behavior. Use a visible test and a targeted probe to localize and verify the repair.

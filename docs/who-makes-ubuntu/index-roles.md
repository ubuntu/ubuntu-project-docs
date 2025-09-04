(roles-and-pathways)=
# Roles and responsibilities

There are many roles and teams that contribute to Ubuntu development. In general,
the roles can be sorted according to the level of upload permissions (and
associated responsibilities). This table summarizes various roles in order of
increasing upload permissions. The three Archive handling teams have the same
level of upload permissions, but different responsibilities. See the sections
below the table for more information on the specific teams. 

```{raw} html
<table border="1" style="border-collapse: collapse; text-align: center; width: 100%;">
  <tr>
    <td><strong>Contributors</strong></td>
    <td style="text-align: left;" colspan="3"><strong>&nbsp;Anyone</strong><br>&nbsp;Report bugs, test fixes, suggest changes</td>
  </tr>
  <tr>
    <!-- Row 2: start of merged col 1 -->
    <td rowspan="3" style="vertical-align: middle;"><strong>Uploaders</strong></td>
    <td style="text-align: left;" colspan="3"><strong>&nbsp;Core Dev</strong><br>&nbsp;Can upload to all packages, can make seed changes</td>
  </tr>
  <tr>
    <td style="text-align: left;" colspan="3"><strong>&nbsp;MOTU</strong><br>&nbsp;Can upload to packages in universe and multiverse</td>
  </tr>
  <tr>
    <td style="text-align: left;" colspan="3"><strong>&nbsp;Per-package / Package Set</strong><br>&nbsp;Can upload to single package(s) or sets of packages</td>
  </tr>
  <tr>
    <!-- Row 1 -->
    <td><strong>Archive<br>handling</strong></td>
    <td><strong>Archive Admin</strong><br>Removals, license checks,<br>fix component mismatches, ...</td>
    <td><strong>MIR member</strong><br>Gates entry to<br>packages in main<br></td>
    <td><strong>SRU member</strong><br>Gates updates to stable<br>releases</td>
  </tr>
</table>
```

## Ubuntu uploaders

```{toctree}
:maxdepth: 1

About uploader roles <about-roles/index-uploaders>
```

## Archive handling

```{toctree}
:maxdepth: 1

about-roles/archive-administration
about-roles/index-MIR
about-roles/index-SRU
```

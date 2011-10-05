
CKAN.Templates.resourceAddLinkFile = ' \
  <form class="resource-add" action=""> \
    <dl> \
      <dt> \
        <label class="field_opt" for="url"> \
          '+CKAN.Strings.fileUrl+' \
        </label> \
      </dt> \
      <dd> \
        <input name="url" type="text" placeholder="http://mydataset.com/file.csv" style="width: 60%"/> \
        <input name="save" type="submit" class="pretty-button primary" value="'+CKAN.Strings.add+'" /> \
        <input name="reset" type="reset" class="pretty-button" value="'+CKAN.Strings.cancel+'" /> \
      </dd> \
    </dl> \
     \
  </form> \
';

CKAN.Templates.resourceAddLinkApi = ' \
  <form class="resource-add" action=""> \
    <dl> \
      <dt> \
        <label class="field_opt" for="url"> \
          '+CKAN.Strings.apiUrl+' \
        </label> \
      </dt> \
      <dd> \
        <input name="url" type="text" placeholder="http://mydataset.com/api/" style="width: 60%" /> \
        <input name="save" type="submit" class="pretty-button primary" value="'+CKAN.Strings.add+'" /> \
        <input name="reset" type="reset" class="pretty-button" value="'+CKAN.Strings.cancel+'" /> \
      </dd> \
    </dl> \
     \
  </form> \
';

CKAN.Templates.resourceUpload = ' \
<div class="fileupload"> \
  <form action="http://test-ckan-net-storage.commondatastorage.googleapis.com/" class="resource-upload" \
    enctype="multipart/form-data" \
    method="POST"> \
 \
    <div class="hidden-inputs"></div> \
    <dl> \
      <dt> \
        <label class="field_opt fileinput-button" for="file"> \
          '+CKAN.Strings.file+' \
        </label> \
      </dt> \
      <dd> \
        <input type="file" name="file" /> \
        <span class="fileinfo"></span> \
        <input id="upload" name="upload" type="submit" class="pretty-button primary" value="'+CKAN.Strings.add+'" /> \
        <input id="reset" name="reset" type="reset" class="pretty-button" value="'+CKAN.Strings.cancel+'" /> \
      </dd> \
    </dl> \
  </form> \
  <div class="messages" style="display: none;"></div> \
  </div> \
</div> \
';



CKAN.Templates.resourceEntry = ' \
  <td class="resource-expand-link"> \
    <a class="resource-expand-link" href="#"><img src="/images/icons/edit-expand.png" /></a> \
    <a class="resource-collapse-link" href="#"><img src="/images/icons/edit-collapse.png" /></a> \
  </td> \
  <td class="resource-summary resource-url"> \
    ${resource.url} \
  </td> \
  <td class="resource-summary resource-name"> \
    ${resource.name} \
  </td> \
  <td class="resource-summary resource-format"> \
    ${resource.format} \
  </td> \
  <td class="resource-expanded" colspan="3"> \
    <div class="inner"> \
    <table> \
      <thead> \
      <th class="form-label"></th> \
      <th class="form-value"></th> \
      <th class="form-label"></th> \
      <th class="form-value"></th> \
      </thead> \
      <tbody> \
      <tr> \
      <td class="form-label">'+CKAN.Strings.name+'</td> \
      <td class="form-value" colspan="3"> \
        <input name="resources__${num}__name" type="text" value="${resource.name}" class="long" /> \
      </td> \
      </tr> \
      <tr> \
      <td class="form-label">'+CKAN.Strings.description+'</td> \
      <td class="form-value" colspan="3"> \
        <input name="resources__${num}__description" type="text" value="${resource.description}" class="long" /> \
      </td> \
      </tr> \
      <tr> \
      <td class="form-label">'+CKAN.Strings.url+'</td> \
      <td class="form-value" colspan="3"> \
      {{if resource.resource_type=="file.upload"}} \
        ${resource.url} \
        <input name="resources__${num}__url" type="hidden" value="${resource.url}" /> \
      {{/if}} \
      {{if resource.resource_type!="file.upload"}} \
        <input name="resources__${num}__url" type="text" value="${resource.url}" class="long" /> \
      {{/if}} \
      </td> \
      </tr> \
      <tr> \
      <td class="form-label">'+CKAN.Strings.format+'</td> \
      <td class="form-value"> \
        <input name="resources__${num}__format" type="text" value="${resource.format}" class="long autocomplete-format" /> \
      </td> \
      <td class="form-label">'+CKAN.Strings.resourceType+'</td> \
      <td class="form-value"> \
      {{if resource.resource_type=="file.upload"}} \
        ${resource.resource_type} \
        <input name="resources__${num}__resource_type" type="hidden" value="${resource.resource_type}" /> \
      {{/if}} \
      {{if resource.resource_type!="file.upload"}} \
        <input name="resources__${num}__resource_type" type="text" value="${resource.resource_type}" /> \
      {{/if}} \
      </td> \
      </tr> \
      <tr> \
      <td class="form-label">'+CKAN.Strings.sizeBracketsBytes+'</td> \
      <td class="form-value"> \
        <input name="resources__${num}__size" type="text" value="${resource.size}" class="long" /> \
      </td> \
      <td class="form-label">'+CKAN.Strings.mimetype+'</td> \
      <td class="form-value"> \
        <input name="resources__${num}__mimetype" type="text" value="${resource.mimetype}" /> \
      </td> \
      </tr> \
      <tr> \
      <td class="form-label">'+CKAN.Strings.lastModified+'</td> \
      <td class="form-value"> \
        <input name="resources__${num}__last_modified" type="text" value="${resource.last_modified}" /> \
      </td> \
      <td class="form-label">'+CKAN.Strings.mimetypeInner+'</td> \
      <td class="form-value"> \
        <input name="resources__${num}__mimetype_inner" type="text" value="${resource.mimetype_inner}" /> \
      </td> \
      </tr> \
      <tr> \
      <td class="form-label">'+CKAN.Strings.hash+'</td> \
      <td class="form-value"> \
        ${resource.hash || "Unknown"} \
        <input name="resources__${num}__hash" type="hidden" value="${resource.hash}" /> \
      </td> \
      <td class="form-label">'+CKAN.Strings.id+'</td> \
      <td class="form-value"> \
        ${resource.id} \
        <input name="resources__${num}__id" type="hidden" value="${resource.id}" /> \
      </td> \
      </tr> \
    </tbody> \
    </table> \
    <button class="delete-resource pretty-button danger">'+CKAN.Strings.deleteResource+'</button> \
    </div> \
  </td> \
  <td class="resource-is-changed"> \
    <img src="/images/icons/add.png" title="'+CKAN.Strings.resourceHasUnsavedChanges+'" class="resource-is-changed" /> \
  </td> \
';
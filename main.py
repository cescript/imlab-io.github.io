# import required modules
# python -m pip install requests
# python -m pip install gitpython
# python -m pip install python-frontmatter
import requests
import git
import os
import frontmatter
import shutil

# simple curl like method to return js object as output
def curl(url):
    content = requests.get(url)
    if content.status_code == requests.codes['ok']:
        return content.json()
    else:
        print(('CODE[{code}]: ' + 'content not fetched from ' + url).format(code=content.status_code))
        return None

# get the repositories starts with 'keyword' of the given user
def get_repositiories_from_user(user_name, keyword):
    
    api_url = 'https://api.github.com'
    api_content = curl(api_url)
    
    # check the api response and find the user urls
    if api_content:
        user_url = api_content['user_url'].format(user=user_name)
        user_content = curl(user_url)
    
        # create list of repositories
        repository_list = []
        
        # if the user content request returned successfully
        if user_content:
            # get the list of the repositories
            repository_content = curl(user_content['repos_url'])
            # if the repositories are fetched, process each one
            if repository_content:
                for single_repo in repository_content:
                    # check that the repository name contains 'keyword'
                    if single_repo['name'].startswith(keyword):
                        repository_list.append({'name': single_repo['name'], 'clone_url': single_repo['clone_url']})
                    
    # return the list of repositories starting with 'keyword'
    return repository_list

# get the repositories starts with 'keyword' of the given user
def get_repositiories_from_organization(organization_name):
    api_url = 'https://api.github.com'
    api_content = curl(api_url)
    
    # check the api response and find the user urls
    if api_content:
        org_url = api_content['organization_url'].format(org=organization_name)
        org_content = curl(org_url)
        
        # create list of repositories
        repository_list = []
        
        # if the user content request returned successfully
        if org_content:
            # get the list of the repositories
            repository_content = curl(org_content['repos_url'])
            # if the repositories are fetched, process each one
            for single_repo in repository_content:
                repository_list.append({'name': single_repo['name'], 'clone_url': single_repo['clone_url']})
    
    # return the list of repositories starting with 'keyword'
    return repository_list


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    repos_list = get_repositiories_from_organization('imlab-io')
    clone_dir = 'temp'
    posts_dir = 'site/_posts'
    assets_dir = 'site/_assets/post_resources'
 
    # make directory to clone repos
    if not os.path.isdir(clone_dir):
        os.mkdir(clone_dir)
    
    # clone repository
    for repo in repos_list:
        print('cloning ' + repo['name'] + ' from ' + repo['clone_url'] + ' ...')
        repository_clone_directory = os.path.join(clone_dir, repo['name'])
        
        # make directory and clone into it
        if os.path.isdir(repository_clone_directory):
            print('will be pulled later!')
        else:
            os.mkdir(repository_clone_directory)
            git.Repo.clone_from(repo['clone_url'], repository_clone_directory)
        
        # set the readme filename
        readme_path = os.path.join(repository_clone_directory, 'readme.md')
        
        # get the content of the readme
        post = frontmatter.load(readme_path)
        
        # copy the cloned content to site
        post_filename = (post.metadata['date'] + '-' + post.metadata['title'] + '.md').replace(' ', '-')
        post_path = os.path.join(posts_dir, post_filename)
        shutil.copyfile(readme_path, post_path)
        
        # copy the assets
        assets_directory = os.path.join(assets_dir, repo['name'])
        